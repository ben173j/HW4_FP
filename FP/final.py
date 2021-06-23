import pyb, sensor, image, time, math

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)  # we run out of memory if the resolution is much bigger...
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()

f_x = (2.8 / 3.984) * 160  # find_apriltags defaults to this if not set
f_y = (2.8 / 2.952) * 120  # find_apriltags defaults to this if not set
c_x = 160 * 0.5  # find_apriltags defaults to this if not set (the image.w * 0.5)
c_y = 120 * 0.5  # find_apriltags defaults to this if not set (the image.h * 0.5)


def degrees(radians):
    return (180 * radians) / math.pi


uart = pyb.UART(3, 9600, timeout_char=1000)
uart.init(9600, bits=8, parity=None, stop=1, timeout_char=1000)
'''
FINISH=0
while FINISH<4:
    FINISH=FINISH+1
    print("not finished FINISH: %d"%FINISH)
    time.sleep(500)
    if FINISH == 2:
        print("FINISH: %d" %FINISH)
        time.sleep(1)
    if FINISH == 3:
        print("FINISH: %d" %FINISH)
        time.sleep(1)
        break
'''
FINISH=0



while(1):
   clock.tick()
   img = sensor.snapshot()
   for tag in img.find_apriltags(fx=f_x, fy=f_y, cx=c_x, cy=c_y): # defaults to TAG36H11
      img.draw_rectangle(tag.rect(), color = (255, 0, 0))
      img.draw_cross(tag.cx(), tag.cy(), color = (0, 255, 0))
      # The conversion is nearly 6.2cm to 1 -> translation
      print_args = (tag.id(), tag.x_translation(), tag.y_translation(), tag.z_translation(), \
            degrees(tag.x_rotation()), degrees(tag.y_rotation()), degrees(tag.z_rotation()))
      # Translation units are unknown. Rotation units are in degrees.
      #print("ID: %d Tx: %f, Ty %f, Tz %f, Rx %f, Ry %f, Rz %f\r\n" %print_args)
      AX =tag.x_translation()
      uart.write(("%1.2f\r\n" %tag.x_translation()).encode())
      print("X : %1.2f" %AX)
      if AX > 0.1:
        time.sleep_ms(30)
        uart.write("1000\r\n".encode())
        print("LEFT AX>0.15, angle: %1.2f" %AX)
        FINISH=0
      elif AX< -0.1:
        time.sleep_ms(30)
        uart.write("1000\r\n".encode())
        print("RIGHT AX<-0.15, angle: %1.2f" %AX)
        FINISH=0
      else:
        if FINISH==2:
            break
        uart.write("2000\r\n".encode())
        print("FINISH, angle: %1.2f" %AX)
        FINISH = FINISH + 1
        print("FINISH_A: %d" %FINISH)
        time.sleep_ms(400)
   if FINISH==2:
      break



print("APRILTAG FINISH")
uart.write("1500\r\n".encode())
time.sleep(8)


      #uart.write(("ID: %d Tx: %f, Ty %f, Tz %f, Rx %f, Ry %f, Rz %f\r\n" %print_args).encode())
      #uart.write(("ID: %d \r\n" %tag.id()).encode())
   #uart.write(("FPS %f\r\n" % clock.fps()).encode())
      #time.sleep_ms(100)





# 跟踪一条黑线。使用[(128,255)]来跟踪白线。
GRAYSCALE_THRESHOLD = [(0, 64)]
# 设置阈值，如果是黑线，GRAYSCALE_THRESHOLD = [(0, 64)]；
# 如果是白线，GRAYSCALE_THRESHOLD = [(128，255)]

ROIS = [  # [ROI, weight]
    (0, 100, 160, 20, 0.1),  # 你需要为你的应用程序调整权重
    (0, 050, 160, 20, 0.3),  # 取决于你的机器人是如何设置的。
    (0, 000, 160, 20, 0.7)
]

# Compute the weight divisor (we're computing this so you don't have to make weights add to 1).
weight_sum = 0  # 权值和初始化
for r in ROIS: weight_sum += r[4]  # r[4] is the roi weight.

sensor.reset()  # 初始化sensor

sensor.set_pixformat(sensor.GRAYSCALE)  # use grayscale.
# 设置图像色彩格式，有RGB565色彩图和GRAYSCALE灰度图两种

sensor.set_framesize(sensor.QQVGA)  # 使用QQVGA的速度。

sensor.skip_frames(30)  # 让新的设置生效。
sensor.set_auto_gain(False)  # 颜色跟踪必须关闭自动增益
sensor.set_auto_whitebal(False)  # 颜色跟踪必须关闭白平衡
clock = time.clock()  # 跟踪FPS帧率

while (True):
    clock.tick()
    img = sensor.snapshot()
    centroid_sum = 0
    AREA=0
    for r in ROIS:
        blobs = img.find_blobs(GRAYSCALE_THRESHOLD, roi=r[0:4], merge=True)
        # r[0:4] is roi tuple.
        # 找到视野中的线,merge=true,将找到的图像区域合并成一个

        # 目标区域找到直线
        if blobs:
            # 查找像素最多的blob的索引。
            largest_blob = 0
            most_pixels = 0
            for i in range(len(blobs)):
                # 目标区域找到的颜色块（线段块）可能不止一个，找到最大的一个，作为本区域内的目标直线
                if blobs[i].pixels() > most_pixels:
                    most_pixels = blobs[i].pixels()
                    # merged_blobs[i][4]是这个颜色块的像素总数，如果此颜色块像素总数大于
                    # most_pixels，则把本区域作为像素总数最大的颜色块。更新most_pixels和largest_blob
                    largest_blob = i

            
            # 在色块周围画一个矩形。
            img.draw_rectangle(blobs[largest_blob].rect())
            AREA_A = blobs[largest_blob].area()
            # 将此区域的像素数最大的颜色块画矩形和十字形标记出来
            img.draw_cross(blobs[largest_blob].cx(),
                           blobs[largest_blob].cy())

            centroid_sum += blobs[largest_blob].cx() * r[4]  # r[4] is the roi weight.
            # 计算centroid_sum，centroid_sum等于每个区域的最大颜色块的中心点的x坐标值乘本区域的权值
    
    
    center_pos = (centroid_sum / weight_sum)  # Determine center of line.
    # 中间公式
    #1300<BLOB< 1800 
    # 将center_pos转换为一个偏角。我们用的是非线性运算，所以越偏离直线，响应越强。
    # 非线性操作很适合用于这样的算法的输出，以引起响应“触发器”。
    deflection_angle = 0
    # 机器人应该转的角度

    # 80是X的一半，60是Y的一半。
    # 下面的等式只是计算三角形的角度，其中三角形的另一边是中心位置与中心的偏差，相邻边是Y的一半。
    # 这样会将角度输出限制在-45至45度左右。（不完全是-45至45度）。

    deflection_angle = -math.atan((center_pos - 80) / 60)
    # 角度计算.80 60 分别为图像宽和高的一半，图像大小为QQVGA 160x120.
    # 注意计算得到的是弧度值

    deflection_angle = math.degrees(deflection_angle)
    # 将计算结果的弧度值转化为角度值

    # 现在你有一个角度来告诉你该如何转动机器人。
    # 通过该角度可以合并最靠近机器人的部分直线和远离机器人的部分直线，以实现更好的预测。

    # print("Turn Angle: %1.2f" % deflection_angle)
    #print("BLOB: %1.2f" %blobs[largest_blob].cx())
    # 将结果打印在terminal中
    # uart.write(("ID: %d Tx: %f, Ty %f, Tz %f, Rx %f, R    y %f, Rz %f\r\n" %print_args).encode())
    # uart.write(("ID: %d \r\n" %tag.id()).encode())

    uart.write("%1.2f\r\n" % deflection_angle)
    if deflection_angle > 38:
        time.sleep_ms(30)
        uart.write("1000\r\n".encode())
        print("Right!Turn Angle: %1.2f" % deflection_angle)
    elif deflection_angle < 21 and 1000<AREA_A<1300:
        uart.write("12\r\n".encode())
        time.sleep(1.7)
        uart.write("1000\r\n".encode())
        print("LONG TURN LEFT! Angle: %1.2f" % deflection_angle)
    elif deflection_angle < 21 and 1000<AREA_A<1300:
        uart.write("50\r\n".encode())
        time.sleep(1.4)
        uart.write("1000\r\n".encode())
        print("LONG TURN RIGHT! Angle: %1.2f" % deflection_angle)
    elif deflection_angle < 14:
        time.sleep_ms(100)
        uart.write("1000\r\n".encode())
        print("Left! Turn Angle: %1.2f" % deflection_angle)
    else:
        time.sleep_ms(100)
        uart.write("1000\r\n".encode())
        print("Straight! Turn Angle: %1.2f" % deflection_angle)
    print("AREA: %1.2f"%AREA_A)
    # uart.write(("FPS %f\r\n" % cclock.fps()).encode())
