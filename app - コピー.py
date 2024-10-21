from flask import Flask, request, send_file, render_template_string
import os
import librosa
import soundfile as sf
from pydub import AudioSegment

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # アップロードされたファイルを保存するフォルダ

# アップロード画面
@app.route('/')
def index():
    return '''
    <h1>Upload an audio file</h1>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <label for="steps">Select pitch shift (in steps):</label>
        <select name="steps">
            <option value="1">+1 step</option>
            <option value="2">+2 steps</option>
            <option value="3">+3 steps</option>
            <option value="4">+4 steps</option>
            <option value="5">+5 steps</option>
            <option value="-1">-1 step</option>
            <option value="-2">-2 steps</option>
            <option value="-3">-3 steps</option>
            <option value="-4">-4 steps</option>
            <option value="-5">-5 steps</option>
        </select>
        <input type="submit" value="Upload and Change Pitch">
    </form>
    '''

# アップロードされたファイルを処理し、音程変更を行う
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    
    if file:
        # アップロードされたファイルを保存
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # 音程変更 (steps で選択された値に基づく)
        steps = int(request.form['steps'])
        new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'changed_{file.filename}')
        
        # 音程を変更し、保存
        change_pitch(file_path, steps, new_file_path)
        
        # 変更後のファイルを返すリンクを生成
        return f'File uploaded and pitch changed successfully! <a href="/download/{new_file_path}">Download here</a>.'


# 音程を変更する関数 (librosaを使用して長さを保持)
def change_pitch(file_path, steps, output_path):
    # 音声ファイルを読み込む
    y, sr = librosa.load(file_path)
    
    # ピッチをシフト（半音単位で調整）
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=steps)
    
    # 変更後の音声ファイルを保存
    sf.write(output_path, y_shifted, sr)

# 変更後のファイルをダウンロードできるようにする
@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
