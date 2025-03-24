import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import json


class ImageClassifier:
    def __init__(self):
        # MobileNet V2 모델 로드 및 평가 모드로 설정
        self.model = models.mobilenet_v2(
            weights=models.MobileNet_V2_Weights.IMAGENET1K_V1
        )
        self.model.eval()

        # 모델 저장
        self.save_model("mobilenet_v2_model.pth")

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

    def save_model(self, model_path):
        """
        학습된 모델을 파일로 저장

        Args:
            model_path (str): 모델을 저장할 파일 경로
        """
        torch.save(self.model.state_dict(), model_path)
        print(f"모델이 {model_path}에 저장되었습니다.")

    def predict(self, image_path, top_k=5):
        """
        이미지 경로를 받아 추론을 수행하고 상위 k개의 예측 결과를 반환

        Args:
            image_path (str): 이미지 파일 경로
            top_k (int): 반환할 상위 예측 개수

        Returns:
            list: (클래스명, 확률) 튜플의 리스트
        """
        # 이미지 로드 및 전처리
        image = Image.open(image_path).convert("RGB")
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


def main():
    # 분류기 초기화
    classifier = ImageClassifier()

    # 이미지 경로 설정
    image_path = "./sample1.png"

    # 예측 수행
    predictions = classifier.predict(image_path, top_k=5)

    # 결과 출력
    print("\n예측 결과:")
    for class_name, probability in predictions:
        print(f"{class_name}: {probability:.4f}")


if __name__ == "__main__":
    main()
