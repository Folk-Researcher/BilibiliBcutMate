from flask import Flask, request, jsonify
import json
import time
import os

app = Flask(__name__)

# 定义项目文件的路径
BCUT_PROJECT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '22-57-16-88--{1c3e00f7-3b2a-4f38-be41-b26bac083b04}.bjson')

@app.route('/api', methods=['POST'])
def handle_api_request():
    """
    统一处理所有发送到 /api 的请求。
    """
    data = request.get_json()

    if not data or 'method' not in data:
        return jsonify({"error": "Invalid request"}), 400

    method = data.get('method')
    params = data.get('params', {})

    if method == 'add_caption':
        return add_caption(params)
    elif method == 'get_project_info':
        return get_project_info(params)
    elif method == 'update_caption':
        return update_caption(params)
    elif method == 'delete_caption':
        return delete_caption(params)
    else:
        return jsonify({"error": f"Method '{method}' not found"}), 404

def add_caption(params):
    """
    向视频项目中添加一条新的字幕。
    """
    text = params.get('text')
    start_time_ms = params.get('start_time_ms', 0)
    duration_ms = params.get('duration_ms', 3000)

    if not text:
        return jsonify({"error": "Missing 'text' parameter"}), 400

    try:
        # 读取现有的项目文件
        with open(BCUT_PROJECT_FILE, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        # 定位到字幕轨道，如果不存在则创建一个
        caption_tracks = project_data['timelineWidget']['timeline']['captionTracks']
        if not caption_tracks:
            # 创建一个新的字幕轨道
            new_track = {
                "captions": [],
                "idString": str(int(time.time() * 1000)),
                "index": 0,
                "trackType": 5  # 假设 5 是字幕轨道的类型
            }
            caption_tracks.append(new_track)
        caption_track = caption_tracks[0]
        captions = caption_track['captions']

        # 创建新的字幕对象
        new_caption = {
            "assetInfo": {
                "assetItemType": 15,
                "content": text,
                "duration": duration_ms,
                "fontID": 0,
                "fontSrcPath": "D:/Programs/BcutBilibili/Font/Source Han Sans CN Medium.ttf",
                "realMaterialId": "-4",
                "type": 4
            },
            "captionText": text,
            "defaultFontName": "思源黑体 CN Medium",
            "defaultFontPath": "D:/Programs/BcutBilibili/Font/Source Han Sans CN Medium.ttf",
            "fontPackagePath": "D:/Programs/BcutBilibili/Font/Source Han Sans CN Medium.ttf",
            "idString": str(int(time.time() * 1000)) + str(int(time.time()*1000000))[-7:],
            "inPoint": start_time_ms,
            "outPoint": start_time_ms + duration_ms,
            "opacity": 1,
            "scaleX": 1,
            "scaleY": 1,
            "textAlignment": 1,
            "textColor": {"a": 1, "b": 1, "g": 1, "r": 1},
            "uid": str(int(time.time() * 1000)) + str(int(time.time()*1000000))[-7:],
        }

        # 将新字幕添加到列表中
        captions.append(new_caption)

        # 写回项目文件
        with open(BCUT_PROJECT_FILE, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=None)

        return jsonify({
            "success": True,
            "message": "Caption added successfully."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_project_info(params):
    """
    获取项目信息，如分辨率、帧率和字幕。
    """
    try:
        with open(BCUT_PROJECT_FILE, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        config = project_data.get('timelineWidget', {}).get('timeline', {}).get('config', {})
        video_res = config.get('videoRes', {})
        video_fps = config.get('videoFps', {})
        
        captions = []
        caption_tracks = project_data.get('timelineWidget', {}).get('timeline', {}).get('captionTracks', [])
        if caption_tracks and len(caption_tracks) > 0:
            captions = caption_tracks[0].get('captions', [])

        project_info = {
            'resolution': {
                'width': video_res.get('width'),
                'height': video_res.get('height')
            },
            'fps': video_fps.get('num'),
            'captions': captions
        }

        return jsonify({
            "success": True,
            "data": project_info
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_caption(params):
    """
    更新现有字幕的内容、开始时间或持续时间。
    """
    caption_id = params.get('id')
    updates = params.get('updates', {})

    if not caption_id or not updates:
        return jsonify({"error": "Missing 'id' or 'updates' parameter"}), 400

    try:
        with open(BCUT_PROJECT_FILE, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        caption_found = False
        caption_tracks = project_data.get('timelineWidget', {}).get('timeline', {}).get('captionTracks', [])
        if caption_tracks and len(caption_tracks) > 0:
            for caption in caption_tracks[0].get('captions', []):
                if caption.get('idString') == caption_id:
                    if 'text' in updates:
                        caption['captionText'] = updates['text']
                        caption['assetInfo']['content'] = updates['text']
                    if 'start_time_ms' in updates:
                        caption['inPoint'] = updates['start_time_ms']
                        # If duration is not updated simultaneously, recalculate outPoint based on old duration
                        if 'duration_ms' not in updates:
                            caption['outPoint'] = updates['start_time_ms'] + caption['assetInfo']['duration']
                    if 'duration_ms' in updates:
                        caption['assetInfo']['duration'] = updates['duration_ms']
                        # Recalculate outPoint based on new duration and potentially new start time
                        caption['outPoint'] = caption['inPoint'] + updates['duration_ms']
                    
                    caption_found = True
                    break
        
        if not caption_found:
            return jsonify({"error": "Caption not found"}), 404

        with open(BCUT_PROJECT_FILE, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=None)

        return jsonify({"success": True, "message": "Caption updated successfully."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def delete_caption(params):
    """
    Deletes an existing caption from the project.
    """
    caption_id = params.get('id')

    if not caption_id:
        return jsonify({"error": "Missing 'id' parameter"}), 400

    try:
        with open(BCUT_PROJECT_FILE, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        caption_found = False
        caption_tracks = project_data.get('timelineWidget', {}).get('timeline', {}).get('captionTracks', [])
        if caption_tracks and len(caption_tracks) > 0:
            captions = caption_tracks[0].get('captions', [])
            caption_to_remove = None
            for caption in captions:
                if caption.get('idString') == caption_id:
                    caption_to_remove = caption
                    break
            
            if caption_to_remove:
                captions.remove(caption_to_remove)
                caption_found = True
        
        if not caption_found:
            return jsonify({"error": "Caption not found"}), 404

        with open(BCUT_PROJECT_FILE, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, ensure_ascii=False, indent=None)

        return jsonify({"success": True, "message": "Caption deleted successfully."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)