import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import json
import io
from typing import List, Tuple
import base64


class ImageClassifier:
    def __init__(self, model_path: str = "./mobilenet_v2_model.pth"):
        # MobileNet V2 모델 로드
        self.model = models.mobilenet_v2(
            weights=None  # 사전 학습된 가중치를 로드하지 않음
        )

        # 저장된 모델 가중치 로드
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

        # GPU 사용 가능 시 GPU로 모델 이동
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)

        # 이미지 전처리를 위한 변환 정의
        self.transform = transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        # ImageNet 클래스 레이블 로드
        with open("imagenet_classes.json", "r") as f:
            self.classes = json.load(f)

    async def predict_image(
        self, image_data: bytes, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        이미지 바이트 데이터를 받아 추론을 수행하고 상위 k개의 예측 결과를 반환

        Args:
            image_data (bytes): 이미지 바이트 데이터
            top_k (int): 반환할 상위 예측 개수

        Returns:
            List[Tuple[str, float]]: (클래스명, 확률) 튜플의 리스트
        """
        # 바이트 데이터로부터 이미지 로드
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0)
        image_tensor = image_tensor.to(self.device)

        # 추론 수행
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

        # 상위 k개 예측 결과 추출
        top_k_prob, top_k_indices = torch.topk(probabilities, top_k)

        # 결과 포맷팅
        predictions = []
        for i in range(top_k):
            class_idx = str(top_k_indices[i].item())
            predictions.append((self.classes[class_idx], float(top_k_prob[i].item())))

        return predictions

    async def predict_base64_image(
        self, base64_string: str, top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Base64 인코딩된 이미지 문자열을 받아 추론을 수행
        """
        try:
            # Base64 디코딩
            image_data = base64.b64decode(base64_string)
            return await self.predict_image(image_data, top_k)
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {str(e)}")
