# import torch
# import cv2
# import ultralytics
# # 加载模型
# #model = torch.hub.load(r'D:\YOLO\yolo_v5_v11\yolo\v11\weights\yolov8m.pt', 'custom', path=r'D:\YOLO\yolo_v5_v11\yolo\v11\runs\detect\train\weights\best.pt')  # 替换为你的best.pt路径
# model = torch.load(r'D:\YOLO\yolo_v5_v11\yolo\v11\runs\detect\train\weights\best.pt')
# # 读取图像
# img_path = r'C:\Users\Administrator\Desktop\images\51.png'  # 替换为你的图像路径
# img = cv2.imread(img_path)
# img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#
# # 进行推理
# results = model(img_rgb)
#
# # 获取检测框和类别信息
# det_boxes = results.xyxy[0].cpu().numpy().astype(int)
# labels = [model.names[int(cls)] for *_, _, cls in det_boxes]
# confidences = [conf for *_, conf, _ in det_boxes]
#
# # 绘制检测框
# for box, label, conf in zip(det_boxes, labels, confidences):
#     x1, y1, x2, y2 = box
#     cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#     cv2.putText(img, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#
# # 显示结果图像
# cv2.imshow('YOLOv8 Detection', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# import torch
# from ultralytics import YOLO
# from PIL import Image
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
#
# # 指定模型路径（可以是.pt或.torchscript文件）
# model_path = r'D:\YOLO\yolo_v5_v11\yolo\v11\runs\detect\train\weights\best.pt'  # 替换为你的模型路径
#
# # 加载YOLOv8模型
# model = YOLO(model_path)
#
# # 加载并预处理图像
# img_path = r'C:\Users\Administrator\Desktop\images\45.png'  # 替换为你的图像路径
# img = Image.open(img_path)
#
# # 进行推理
# results = model(img)
# print("-----------")
# print(results)
# print("-----------")
#
# fig, ax = plt.subplots(1, figsize=(img.width / 100, img.height / 100))  # 设置图像大小与原图比例相同
# ax.imshow(img)
#
# # 遍历检测结果（注意：这里假设results.pred包含了所有需要的信息）
# # 注意：results.pred的结构可能因YOLO版本而异，请查阅文档确认
# for pred in results.pred[0]:  # 假设results.pred[0]包含第一批结果
#     xyxy = pred[0:4]  # 边界框坐标（xmin, ymin, xmax, ymax）
#     conf = pred[4]  # 置信度
#     cls = int(pred[5])  # 类别ID
#     label = f'{model.names[cls]} {conf:.2f}'  # 创建标签
#
#     # 绘制矩形框
#     rect = patches.Rectangle((xyxy[0], xyxy[1]), xyxy[2] - xyxy[0], xyxy[3] - xyxy[1], linewidth=2, edgecolor='r',
#                              facecolor='none')
#     ax.add_patch(rect)
#
#     # 绘制标签（可能需要调整位置以避免重叠）
#     ax.text(xyxy[0], xyxy[1] - 10, label, color='white', fontsize=12, bbox=dict(facecolor='blue', alpha=0.5))
#
# # 隐藏坐标轴
# ax.axis('off')
#
# # 显示图像
# plt.show()


import ultralytics as yt

# 加载模型
model = yt.load(r'D:\YOLO\yolo_v5_v11\yolo\v11\runs\detect\train\weights\best.pt')  # 替换为您的模型路径

# 加载图像
img_path = r'C:\Users\Administrator\Desktop\images\45.png'  # 替换为您的图像路径
img = yt.Image(img_path)

# 进行推理
results = model(img)

# 绘制结果
results.show()  # 这将使用 YOLOv8 的内置绘图功能显示结果

# 如果您想手动绘制结果，可以使用以下代码：
# 注意：这里的代码取决于 YOLOv8 返回的结果结构
# for res in results.xyxy[0]:  # 假设 results.xyxy 是一个包含检测结果的列表
#     x1, y1, x2, y2, conf, cls = res  # 边界框坐标、置信度和类别 ID
#     # 在这里添加绘制代码，例如使用 matplotlib 或其他绘图库