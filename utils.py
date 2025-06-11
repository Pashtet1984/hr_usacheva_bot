import os
import openpyxl

def save_application(data):
    folder = "data"
    file_path = os.path.join(folder, "applications.xlsx")

    if not os.path.exists(folder):
        os.mkdir(folder)

    if not os.path.exists(file_path):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = "Заявки"
        sheet.append(["Имя", "Email", "Телефон", "Комментарий"])
        wb.save(file_path)

    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
    sheet.append([
        data.get("name"),
        data.get("email"),
        data.get("phone"),
        data.get("comment")
    ])
    wb.save(file_path)
