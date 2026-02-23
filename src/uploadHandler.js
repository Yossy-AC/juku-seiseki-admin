// ===== ファイルアップロード処理 =====

let parsedData = [];
let currentFile = null;

// ページ読み込み
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadStudentsList();
});

// イベントリスナー設定
function setupEventListeners() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // クリック時
    uploadArea.addEventListener('click', () => fileInput.click());

    // ドラッグ&ドロップ
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    // ファイル選択
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

// ファイル処理
async function handleFiles(files) {
    if (files.length === 0) return;

    const file = files[0];
    console.log('Selected file:', file.name, file.type);

    try {
        let csvText;

        if (file.name.endsWith('.csv')) {
            // CSV ファイル
            csvText = await file.text();
        } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
            // Excel ファイル（警告）
            alert('Excel ファイルは、Excel の「名前をつけて保存」で CSV 形式に保存してからアップロードしてください。\n\nステップ:\n1. ファイルを開く\n2. 「名前をつけて保存」\n3. ファイル形式を「CSV (カンマ区切り)」に選択\n4. このページにアップロード');
            return;
        } else {
            alert('CSV または Excel ファイルを選択してください');
            return;
        }

        // CSV を解析
        parsedData = CSVParser.parseCSV(csvText);
        console.log('Parsed data:', parsedData);

        // バリデーション
        validateData(parsedData);

        // プレビュー表示
        displayPreview(parsedData);
        document.getElementById('saveBtn').style.display = 'block';

        currentFile = file;
        showMessage(`${parsedData.length} 件の生徒データが読み込まれました`, 'success');
    } catch (error) {
        console.error('Error:', error);
        showMessage(`エラー: ${error.message}`, 'error');
    }
}

// データの検証
function validateData(data) {
    const requiredFields = ['氏名', '高校', '性別', '学年', '志望大学', '講座ID'];

    for (const row of data) {
        for (const field of requiredFields) {
            if (!row[field] || row[field].trim() === '') {
                throw new Error(`${field}が入力されていない行があります`);
            }
        }

        // 学年は数字チェック
        if (!/^[1-3]$/.test(row['学年'])) {
            throw new Error(`学年は1, 2, 3のいずれかを入力してください`);
        }

        // 性別チェック
        if (!['男', '女'].includes(row['性別'])) {
            throw new Error(`性別は「男」または「女」を入力してください`);
        }
    }
}

// プレビュー表示
function displayPreview(data) {
    const tbody = document.getElementById('previewBody');
    tbody.innerHTML = '';

    data.slice(0, 10).forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row['氏名']}</td>
            <td>${row['高校']}</td>
            <td>${row['性別']}</td>
            <td>${row['学年']}</td>
            <td>${row['志望大学']}</td>
            <td>${row['講座ID']}</td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('previewTable').classList.add('show');
}

// データを保存
async function saveData() {
    if (parsedData.length === 0) {
        alert('データを読み込んでください');
        return;
    }

    try {
        // ローカルストレージに保存
        const existingData = JSON.parse(localStorage.getItem('studentData')) || [];
        const allData = [...existingData];

        // 新規生徒を追加（ID は自動生成）
        let maxId = 0;
        allData.forEach(s => {
            const idNum = parseInt(s.id.replace('s', ''));
            if (idNum > maxId) maxId = idNum;
        });

        parsedData.forEach((row, index) => {
            const newStudent = {
                id: `s${maxId + index + 1}`,
                name: row['氏名'],
                highSchool: row['高校'],
                gender: row['性別'],
                grade: row['学年'],
                targetUniversity: row['志望大学'],
                classId: row['講座ID'],
                joinDate: new Date().toISOString().split('T')[0]
            };
            allData.push(newStudent);
        });

        // ローカルストレージに保存
        localStorage.setItem('studentData', JSON.stringify(allData));
        
        // data/students.json にもコピー（手動で GitHub に Push）
        console.log('Updated students:', allData);

        showMessage(`✅ ${parsedData.length} 件の生徒データを保存しました！`, 'success');
        
        // リセット
        setTimeout(() => {
            clearFile();
            loadStudentsList();
        }, 2000);

    } catch (error) {
        console.error('Error saving data:', error);
        showMessage(`保存エラー: ${error.message}`, 'error');
    }
}

// ファイルをクリア
function clearFile() {
    document.getElementById('fileInput').value = '';
    document.getElementById('previewTable').classList.remove('show');
    document.getElementById('saveBtn').style.display = 'none';
    document.getElementById('message').classList.remove('show');
    parsedData = [];
    currentFile = null;
}

// メッセージ表示
function showMessage(text, type) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = `message show ${type}`;
}

// 学生一覧を読み込んで表示
function loadStudentsList() {
    const tbody = document.getElementById('studentListBody');
    tbody.innerHTML = '';

    // ローカルストレージから読み込む
    const data = JSON.parse(localStorage.getItem('studentData')) || [];

    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">生徒がまだ登録されていません</td></tr>';
        return;
    }

    data.forEach(student => {
        const tr = document.createElement('tr');
        const classInfo = getClassNameById(student.classId); // 簡易版
        tr.innerHTML = `
            <td>${student.name}</td>
            <td>${student.highSchool}</td>
            <td>${student.grade}</td>
            <td>${student.targetUniversity}</td>
            <td>${classInfo || student.classId}</td>
        `;
        tbody.appendChild(tr);
    });
}

// 講座名を取得（簡易版）
function getClassNameById(classId) {
    const classMap = {
        'class001': '高3英語@難関大',
        'class002': '高3英語@共通テスト',
        'class003': '高2英語@標準',
        'class004': '高2英語@発展',
        'class005': '高1英語@基礎',
        'class006': '高1英語@標準',
        'class007': '英検対策'
    };
    return classMap[classId];
}

// テンプレートをダウンロード
function downloadTemplate() {
    const csv = CSVParser.generateTemplate();
    CSVParser.downloadCSV('生徒データテンプレート.csv', csv);
}
