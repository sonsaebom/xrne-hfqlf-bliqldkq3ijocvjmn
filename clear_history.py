
if __name__ == "__main__":
    from dialog.prompt_state import pm
    pm.reset()
    print("✅ 대화 이력이 초기화되었습니다.")


# 해당 파일만 파이썬으로 실행하면 대화 이력이 완전히 초기화됨
# 수동 실행을 위한 방법으로 코딩
# 그렇기에 다른 곳에 호출하는 것은 매우 위험 -> 자동 초기화됨
# 그래서 혹시 몰라서 다른 모듈이 import 하더라도 자동 실행되지 않도록 보호 처리해 둠

