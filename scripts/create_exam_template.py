from openpyxl import Workbook

wb = Workbook()
ws = wb.active
ws.title = 'ImportQuestions'
headers = ['question_type', 'question_text', 'points', 'options_data', 'correct_answer', 'explanation']
ws.append(headers)
ws.append([
    'MCQ',
    'Apa warna bendera Indonesia?',
    '1',
    '{"A": "Merah Putih", "B": "Putih Merah", "C": "Merah Kuning", "D": "Biru Putih"}',
    'A',
    'Bendera Indonesia adalah Merah Putih.'
])
ws.append([
    'TF',
    'Bumi mengelilingi Matahari.',
    '1',
    '',
    'True',
    'Benar, Bumi mengelilingi Matahari.'
])
ws.append([
    'ESSAY',
    'Jelaskan cara kerja fotosintesis secara singkat.',
    '2',
    '',
    '',
    'Fotosintesis mengubah cahaya menjadi energi kimia di daun.'
])
ws.append([
    'MCQ',
    'Pilih hasil dari 2 + 3.',
    '1',
    '{"A": "4", "B": "5", "C": "6", "D": "7"}',
    'B',
    'Hasil penjumlahan 2 + 3 adalah 5.'
])
wb.save('exam_import_template.xlsx')
