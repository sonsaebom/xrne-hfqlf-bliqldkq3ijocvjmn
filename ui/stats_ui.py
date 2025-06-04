import pandas as pd
import pygame
from datetime import datetime, timedelta
import math
from config import (
    CSV_LOG_PATH, EMOTION_STATS_COLORS, EMOTION_LABELS, load_fonts
)


def run_stats_screen():
    # CSV 읽기 및 정제
    df = pd.read_csv(CSV_LOG_PATH)
    df.columns = [col.strip().lower() for col in df.columns]
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d", errors='coerce').dt.date
    df.dropna(subset=['date'], inplace=True)

    # 최근 7일 데이터 필터링
    today = datetime.now().date()
    week_df = df[(df['date'] >= today - timedelta(days=6)) & (df['date'] <= today)]

    # 감정 통계 집계
    emotion_counts = week_df['emotion'].value_counts()

    # 감정 기록이 없는 경우 대비
    if emotion_counts.sum() == 0:
        print("❗ 최근 7일 간 감정 기록이 없습니다.")
        return "base"

    emotion_ratios = emotion_counts / emotion_counts.sum()

    sorted_counts = dict(sorted(emotion_counts.to_dict().items(), key=lambda item: item[1], reverse=True))
    sorted_ratios = dict(sorted(emotion_ratios.to_dict().items(), key=lambda item: item[1], reverse=True))

    # 일자별 대표 감정 계산
    daily_emotion = week_df.groupby('date')['emotion'].agg(
        lambda x: ','.join(sorted(x.mode().astype(str))) if not x.mode().empty else "unknown"
    ).reset_index()

    # 일자 누락 보완
    all_days = pd.date_range(end=today, periods=7).date
    daily_emotion = pd.DataFrame({'date': all_days}).merge(daily_emotion, on='date', how='left')
    daily_emotion['emotion'].fillna("unknown", inplace=True)

    # Pygame 초기화
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("감정 통계")

    font, small_font = load_fonts()
    if not font or not small_font:
        print("❗ 폰트 로딩 실패")
        return "base"

    back_button_rect = pygame.Rect(20, 20, 40, 40)

    def draw_back_button():
        arrow_surface = small_font.render("←", True, (255, 255, 255))
        screen.blit(arrow_surface, (back_button_rect.x + 5, back_button_rect.y))

    def draw_pie(center, radius, data, colors):
        total = sum(data.values())
        angle_start = 0
        for emotion, count in data.items():
            ratio = count / total
            angle_end = angle_start + ratio * 360
            color = colors.get(emotion, (180, 180, 180))
            points = [center]
            for angle in range(int(angle_start), int(angle_end) + 1):
                rad = math.radians(angle)
                x = center[0] + radius * math.cos(rad)
                y = center[1] + radius * math.sin(rad)
                points.append((x, y))
            pygame.draw.polygon(screen, color, points)
            angle_start = angle_end

    def draw_legend(x, y_base, data, colors, labels, line_height=28):
        y = 200 - len(data) * line_height // 2
        for i, (emotion, ratio) in enumerate(data.items()):
            color = colors.get(emotion, (255, 255, 255))
            label_text = f"{labels.get(emotion, emotion)} ({ratio * 100:.1f}%)"
            label_surface = small_font.render(label_text, True, color)
            screen.blit(label_surface, (x, y + i * line_height))

    def draw_daily_boxes(data, labels, box_w=110, box_h=60, gap=0):
        x_start = (800 - (len(data) * (box_w + gap))) // 2
        y = 360
        for i, row in enumerate(data.itertuples()):
            x = x_start + i * (box_w + gap)
            pygame.draw.rect(screen, (255, 255, 255), (x, y, box_w, box_h), 2)
            date_str = row.date.strftime("%m/%d")
            emotion_keys = [e.strip() for e in row.emotion.split(",")]
            label_str = ', '.join([labels.get(e, e) for e in emotion_keys])
            date_surf = small_font.render(date_str, True, (255, 255, 255))
            label_surf = small_font.render(label_str, True, (255, 255, 255))
            screen.blit(date_surf, (x + (box_w - date_surf.get_width()) // 2, y + 8))
            screen.blit(label_surf, (x + (box_w - label_surf.get_width()) // 2, y + 30))

    # UI 그리기
    screen.fill((0, 0, 0))
    draw_back_button()
    title_surface = font.render("감정 통계", True, (255, 255, 255))
    screen.blit(title_surface, ((800 - title_surface.get_width()) // 2, 20))
    draw_pie(center=(230, 200), radius=110, data=sorted_counts, colors=EMOTION_STATS_COLORS)
    draw_legend(x=460, y_base=140, data=sorted_ratios, colors=EMOTION_STATS_COLORS, labels=EMOTION_LABELS)
    draw_daily_boxes(data=daily_emotion, labels=EMOTION_LABELS)
    pygame.display.flip()

    # 이벤트 루프
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                result = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button_rect.collidepoint(event.pos):
                    running = False
                    result = "base"

    return result


