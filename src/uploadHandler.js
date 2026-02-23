// ===== ファイルアップロード処理 =====

let parsedStudentData = [];
let parsedGradeData = [];
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
            csvText = await file.text();
        } else if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
            alert('Excel ファイルは、Excel の「名前をつけて保存」で CSV 形式に保存してからアップロードしてください。');
            return;
        } else {
            alert('CSV または Excel ファイルを選択してください');
            return;
        }

        // CSV を解析（新フォーマット対応）
        const { students, grades } = parseNewFormatCSV(csvText);
        
        parsedStudentData = students;
        parsedGradeData = grades;

        console.log('Parsed students:', parsedStudentData);
        console.log('Parsed grades:', parsedGradeData);

        // プレビュー表示
        displayPreview(parsedStudentData, parsedGradeData);
        document.getElementById('saveBtn').style.display = 'block';

        currentFile = file;
        showMessage(`生徒データ ${parsedStudentData.length} 件、テスト成績 ${parsedGradeData.length} 件が読み込まれました`, 'success');
    } catch (error) {
        console.error('Error:', error);
        showMessage(`エラー: ${error.message}`, 'error');
    }
}

// 新フォーマット CSV を解析
function parseNewFormatCSV(text) {
    const lines = text.trim().split('\n');
    
    let students = [];
    let grades = [];
    let currentSection = null;
    let studentHeaderIndex = -1;
    let gradeHeaderIndex = -1;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        if (line === '【生徒データ】セクション' || line === '【生徒データ】') {
            currentSection = 'students';
            continue;
        } else if (line === '【チェックテスト成績】セクション' || line === '【チェックテスト成績】') {
            currentSection = 'grades';
            continue;
        } else if (line === '') {
            continue;
        }

        if (currentSection === 'students') {
            if (line.includes(',') && studentHeaderIndex === -1) {
                // ヘッダー行
                const headers = CSVParser.parseCSVLine(line);
                studentHeaderIndex = i;
                continue;
            } else if (studentHeaderIndex !== -1 && line.includes(',')) {
                // データ行
                const values = CSVParser.parseCSVLine(line);
                if (values.length >= 11) {
                    const student = {
                        studentCode: values[0],
                        classroom: values[1],
                        name: values[2],
                        nameKana: values[3],
                        gender: values[4],
                        highSchool: values[5],
                        courseSubject: values[6],
                        schoolClass: values[7],
                        club: values[8],
                        targetUniversity: values[9],
                        targetDept: values[10]
                    };
                    students.push(student);
                }
            }
        } else if (currentSection === 'grades') {
            if (line.includes(',') && gradeHeaderIndex === -1) {
                // ヘッダー行
                const headers = CSVParser.parseCSVLine(line);
                gradeHeaderIndex = i;
                continue;
            } else if (gradeHeaderIndex !== -1 && line.includes(',')) {
                // データ行
                const values = CSVParser.parseCSVLine(line);
                if (values.length >= 10) {
                    const grade = {
                        name: values[0],
                        lessonNumber: parseInt(values[1]) || 0,
                        lessonContent: values[2],
                        date: values[3],
                        comprehension: parseInt(values[4]) || 0,
                        unseenProblems: parseInt(values[5]) || 0,
                        grammar: parseInt(values[6]) || 0,
                        vocabulary: parseInt(values[7]) || 0,
                        listening: parseInt(values[8]) || 0,
                        total: parseInt(values[9]) || 0
                    };
                    grades.push(grade);
                }
            }
        }
    }

    if (students.length === 0) {
        throw new Error('【生徒データ】セクションが見つかるか、データが空です');
    }

    return { students, grades };
}

// プレビュー表示
function displayPreview(students, grades) {
    const tbody = document.getElementById('previewBody');
    tbody.innerHTML = '';

    // 生徒データ表示
    students.slice(0, 5).forEach(student => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${student.name}</td>
            <td>${student.highSchool}</td>
            <td>${student.gender}</td>
            <td>${student.courseSubject}</td>
            <td>${student.targetUniversity}</td>
            <td>${student.targetDept}</td>
        `;
        tbody.appendChild(tr);
    });

    if (students.length > 5) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="6" style="text-align: center; color: #999;">他 ${students.length - 5} 件</td>`;
        tbody.appendChild(tr);
    }

    // テスト成績の簡単な概要を表示
    if (grades.length > 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td colspan="6" style="background: #f0f0f0;"><strong>テスト成績: ${grades.length} 件</strong></td>`;
        tbody.appendChild(tr);
    }
}

// データを保存
async function saveData() {
    if (parsedStudentData.length === 0) {
        alert('データを読み込んでください');
        return;
    }

    try {
        const existingStudents = JSON.parse(localStorage.getItem('studentData')) || [];
        const existingGrades = JSON.parse(localStorage.getItem('gradeData')) || [];

        let maxStudentId = 0;
        existingStudents.forEach(s => {
            const idNum = parseInt(s.id?.replace('s', '') || '0');
            if (idNum > maxStudentId) maxStudentId = idNum;
        });

        let addedCount = 0;
        let updatedCount = 0;

        // 生徒データを追加または更新
        parsedStudentData.forEach((student) => {
            const existingIndex = existingStudents.findIndex(s => s.studentCode === student.studentCode);

            if (existingIndex !== -1) {
                // 既存生徒を更新
                existingStudents[existingIndex] = {
                    ...existingStudents[existingIndex],
                    classroom: student.classroom,
                    name: student.name,
                    nameKana: student.nameKana,
                    gender: student.gender,
                    highSchool: student.highSchool,
                    courseSubject: student.courseSubject,
                    schoolClass: student.schoolClass,
                    club: student.club,
                    targetUniversity: student.targetUniversity,
                    targetDept: student.targetDept
                };
                updatedCount++;
            } else {
                // 新規生徒を追加
                maxStudentId++;
                const newStudent = {
                    id: `s${maxStudentId}`,
                    ...student,
                    classId: 'class001',
                    joinDate: new Date().toISOString().split('T')[0]
                };
                existingStudents.push(newStudent);
                addedCount++;
            }
        });

        // テスト成績を追加
        let maxGradeId = 0;
        existingGrades.forEach(g => {
            const idNum = parseInt(g.id?.replace('g', '') || '0');
            if (idNum > maxGradeId) maxGradeId = idNum;
        });

        parsedGradeData.forEach((grade, index) => {
            const matchedStudent = existingStudents.find(s => s.name === grade.name);
            if (matchedStudent) {
                const newGrade = {
                    id: `g${maxGradeId + index + 1}`,
                    studentId: matchedStudent.id,
                    classId: 'class001',
                    lessonNumber: grade.lessonNumber,
                    lessonContent: grade.lessonContent,
                    date: grade.date,
                    scores: {
                        comprehension: grade.comprehension,
                        unseenProblems: grade.unseenProblems,
                        grammar: grade.grammar,
                        vocabulary: grade.vocabulary,
                        listening: grade.listening,
                        total: grade.total
                    },
                    maxScores: {
                        comprehension: 20,
                        unseenProblems: 20,
                        grammar: 20,
                        vocabulary: 20,
                        listening: 20,
                        total: 100
                    }
                };
                existingGrades.push(newGrade);
            }
        });

        localStorage.setItem('studentData', JSON.stringify(existingStudents));
        localStorage.setItem('gradeData', JSON.stringify(existingGrades));

        console.log('Updated students:', existingStudents);
        console.log('Updated grades:', existingGrades);

        showMessage(`生徒データ 新規${addedCount}件、更新${updatedCount}件、テスト成績${parsedGradeData.length}件を保存しました`, 'success');

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
    parsedStudentData = [];
    parsedGradeData = [];
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
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">生徒がまだ登録されていません</td></tr>';
        return;
    }

    data.forEach(student => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${student.name}</td>
            <td>${student.highSchool}</td>
            <td>${student.courseSubject}</td>
            <td>${student.targetUniversity}</td>
            <td>${student.targetDept}</td>
            <td>${student.classroom}</td>
        `;
        tbody.appendChild(tr);
    });
}

// テンプレートをダウンロード
function downloadTemplate() {
    const csv = CSVParser.generateTemplate();
    CSVParser.downloadCSV('生徒データテンプレート.csv', csv);
}

