from ultralytics import YOLO
import os
import time

def load_model(model_path):
    """Load the YOLO model from the given path."""
    return YOLO(model_path)

def run_inference(model, image_path):
    """Run inference on the image using the model."""
    return model(image_path)

def print_results(results, model):
    """Print the detection results to the console."""
    print("Detections:")
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls)
            confidence = float(box.conf)
            bbox = box.xyxy.tolist()[0]  # [x1, y1, x2, y2]
            class_name = model.names[class_id]
            print(f"Class: {class_name}, Confidence: {confidence:.2f}, BBox: {bbox}")

def save_results(results, model, txt_file='detection_results.txt', img_file='detection_result.jpg'):
    """Save the detection results to a text file and annotated image."""
    with open(txt_file, 'w') as f:
        f.write("Detections:\n")
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls)
                confidence = float(box.conf)
                bbox = box.xyxy.tolist()[0]
                class_name = model.names[class_id]
                f.write(f"Class: {class_name}, Confidence: {confidence:.2f}, BBox: {bbox}\n")

    for result in results:
        result.save(img_file)

    print(f"Results saved to {txt_file} and {img_file}")

if __name__ == "__main__":
    # model_path = os.path.join(os.path.dirname(__file__), 'yolo26n.pt') # PyTorch model
    model_path = os.path.join(os.path.dirname(__file__), 'yolo26n_ncnn_model') # NCNN model

    model = load_model(model_path)
    bus_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'img', 'bus.jpg')
    
    times = []
    for i in range(6):
        start = time.time()
        results = run_inference(model, bus_image_path)
        end = time.time()
        latency = end - start
        times.append(latency)
        print(f"Run {i+1}: {latency:.4f}s")
    
    # Average latency for last 5 runs
    avg_latency = sum(times[1:]) / 5
    print(f"Average latency for last 5 runs: {avg_latency:.4f}s")
    
    # Print and save results from the last run
    print_results(results, model)
    save_results(results, model)