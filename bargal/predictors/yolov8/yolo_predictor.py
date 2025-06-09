import cv2
from ultralytics import YOLO
import os
import numpy as np
from pathlib import Path

from bargal.predictors.base import BasePredictor
from bargal.preprocessing import GRLOG_GR_DIFF

this_dir, this_filename = os.path.split(__file__)
base_path = Path(this_dir)

# === Umbral de confianza mínimo ===
CONFIDENCE_THRESHOLD = 0.36

# === Rutas ===
model_paths = [
    base_path / Path('best_v8s_LogDiff.pt'),
    base_path / Path('best_v8m_LogDiff.pt'),
    base_path / Path('best_v8l_LogDiff.pt'),
    base_path / Path('best_v8x_LogDiff.pt')
]

class YoloPredictor(BasePredictor):
    def __init__(self, img_client):
        super().__init__(img_client)
        self._img_processor = GRLOG_GR_DIFF

        self._models = [YOLO(p) for p in model_paths]
        self._img_height = 640
        self._img_width = 640

    def _prepare_features(self, obs):
        img = self._img_processor.preprocess(obs)
        img = (img * 255).astype(np.uint8)

        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    def _predict(self, features) -> bool:
        results_list = [model(features, verbose=False)[0] for model in self._models]
        final_detections = self.__ensemble_predictions(results_list)

        return len(final_detections) > 0

    @classmethod
    def __iou(cls, box1, box2):
        xA, yA = max(box1[0], box2[0]), max(box1[1], box2[1])
        xB, yB = min(box1[2], box2[2]), min(box1[3], box2[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        box1Area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2Area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        return interArea / float(box1Area + box2Area - interArea + 1e-6)

    @classmethod
    def __ensemble_predictions(cls, results_list, iou_thr=0.1, vote_threshold=2):
        all_boxes = []
        for model_idx, result in enumerate(results_list):
            for box in result.boxes:
                conf = box.conf[0].cpu().item()
                if conf < CONFIDENCE_THRESHOLD:
                    continue  # Filtrar detecciones de baja confianza

                coords = box.xyxy[0].cpu().numpy()
                _cls = int(box.cls[0].cpu().item())
                all_boxes.append((coords, conf, _cls, model_idx))  # incluir ID del modelo

        grouped = []
        used = set()

        for i in range(len(all_boxes)):
            if i in used:
                continue
            group = [all_boxes[i]]
            model_ids = {all_boxes[i][3]}

            for j in range(i + 1, len(all_boxes)):
                if j in used:
                    continue
                if all_boxes[i][2] == all_boxes[j][2] and cls.__iou(all_boxes[i][0], all_boxes[j][0]) >= iou_thr:
                    if all_boxes[j][3] not in model_ids:
                        group.append(all_boxes[j])
                        model_ids.add(all_boxes[j][3])
                        used.add(j)
            used.add(i)

            if len(model_ids) >= vote_threshold:
                boxes_np = np.array([g[0] for g in group])
                avg_box = boxes_np.mean(axis=0)
                avg_conf = np.mean([g[1] for g in group])
                _cls = group[0][2]
                grouped.append((avg_box, avg_conf, _cls, len(model_ids)))

        # Validar conflictos
        final_detections = []
        for i, (box_i, conf_i, cls_i, votes_i) in enumerate(grouped):
            conflict = False
            for j, (box_j, conf_j, cls_j, votes_j) in enumerate(grouped):
                if i == j:
                    continue
                if cls.__iou(box_i, box_j) >= iou_thr and cls_i != cls_j:
                    if votes_i > votes_j or (votes_i == votes_j and conf_i > conf_j):
                        continue
                    else:
                        conflict = True
                        break
            if not conflict:
                final_detections.append((box_i, conf_i, cls_i, votes_i))

        return final_detections