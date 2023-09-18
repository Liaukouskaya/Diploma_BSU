import cv2
import numpy as np
import pyperclip
import pandas as pd

# Загружаем изображение
img = cv2.imread('images/image.jpg')

# Уменьшаем масштаб изображения в 1.5 раза
img = cv2.resize(img, None, fx=0.35, fy=0.35)

# Создаем окно для отображения изображения
cv2.namedWindow('image')

# Инициализируем переменную drawing
drawing = False

# Переменная для хранения эталонной длины
ref_len_cm = None
cm_len_list = []


def display_results(results):
    # Создаем пустой массив для хранения данных
    data = []

    # Преобразуем каждый результат в кортеж и добавляем его в список данных
    for i, result in enumerate(results):
        data.append((i + 1, f'{result:.4f}'))

    # Создаем DataFrame из списка данных
    df = pd.DataFrame(data, columns=['Num  ', 'Length'])

    # Создаем изображение белого цвета размером 400x600
    img = 255 * np.zeros((600, 400, 3), dtype=np.uint8)

    # Определяем размер и цвет текста
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4
    font_color = (255, 255, 255)

    # Добавляем заголовок таблицы
    cv2.putText(img, 'Measurement results', (5, 30), font, font_scale, font_color, 1, cv2.LINE_AA)

    # Отображаем DataFrame на изображении
    table_string = df.to_string(index=False, justify='center')
    lines = table_string.split('\n')
    line_height = int(img.shape[0] / len(lines))
    for i, line in enumerate(lines):
        y = int((i + 1) * line_height)
        x = int(img.shape[1] * 0.1)
        cv2.putText(img, line, (x, y), font, font_scale, font_color, 1, cv2.LINE_AA)

    # # Добавляем горизонтальные линии в таблицу
    # thickness = 1
    # y = line_height
    # cv2.line(img, (0, y), (img.shape[1], y), (0, 0, 0), thickness)
    # for i in range(len(lines) - 1):
    #     y += line_height
    #     cv2.line(img, (0, y), (img.shape[1], y), (0, 0, 0), thickness)

    # Отображаем изображение с таблицей в окне
    cv2.namedWindow('Results', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Results', 400, 600)
    cv2.imshow('Results', img)

    while True:
        key = cv2.waitKey(0)
        if key == 27:  # Escape key
            break
        elif key == ord('s'):  # "s" key
            pyperclip.copy(table_string)
            print('Values copied to clipboard.')
            break

    cv2.destroyAllWindows()


# Функция для обработки событий мыши
def draw_line(event, x, y, flags, param):
    global ix, iy, drawing, ref_len_cm, cm_len_list, line_coords

    # Обрабатываем нажатие левой кнопки мыши
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        line_coords = [(ix, iy)]

    # Обрабатываем перемещение мыши
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            # Добавляем новую точку на линию
            line_coords.append((x, y))

            # Отображаем линию на изображении
            img_copy = img.copy()
            cv2.polylines(img_copy, [np.array(line_coords)], False, (0, 255, 255), 2)
            cv2.imshow('image', img_copy)

    # Обрабатываем отпускание левой кнопки мыши
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cv2.polylines(img, [np.array(line_coords)], False, (0, 255, 255), 2)
        cv2.imshow('image', img)

        # Вычисляем длину отрезка в пикселях
        pixel_len = np.sqrt((x - ix) ** 2 + (y - iy) ** 2)

        # Проверяем, была ли нажата правая кнопка мыши
        if flags == cv2.EVENT_FLAG_RBUTTON:
            # Вычисляем длину отрезка в сантиметрах и сохраняем ее в ref_len_cm
            ref_len_cm = pixel_len
            print('Эталонная длина: {:.4f} пикселей'.format(ref_len_cm))

        else:
            if ref_len_cm is None:
                print('Эталонная длина не задана')
            elif ref_len_cm == 0:
                print('Ошибка: эталонная длина равна 0')
            else:
                # Вычисляем длину отрезка в сантиметрах, используя эталонную длину
                cm_len = (pixel_len / ref_len_cm) * 1.0
                print('Длина корня: {:.4f} см'.format(cm_len))
                cm_len_list.append(cm_len)
                display_results(cm_len_list)


# Создаем окно с изображением и назначаем обработчик событий мыши
cv2.imshow('image', img)
cv2.setMouseCallback('image', draw_line)

cv2.waitKey(0)
cv2.destroyAllWindows()
