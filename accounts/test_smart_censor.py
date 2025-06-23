from utils import smart_censor_text
import time

def test_smart_censor():
    # Тестовые фразы
    test_phrases = [
        "Это нормальный текст",
        "Это блять тестовый текст",
        "Хуй знает что тут написано",
        "Пиздец какой-то",
        "Охуеть можно",
        "Нахуй иди",
        "Сука блять",
        "Ебать ты лох",
        "Это очень интересный рецепт",
        "Вкусный пирог получился",
    ]
    
    print("Тестирование умной цензуры:")
    print("-" * 50)
    
    for phrase in test_phrases:
        print(f"\nОригинал: {phrase}")
        censored = smart_censor_text(phrase)
        print(f"После цензуры: {censored}")
        print("-" * 50)
        time.sleep(1)  # Задержка между тестами

if __name__ == "__main__":
    test_smart_censor() 