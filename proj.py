import customtkinter as ctk
import math
import re
from tkinter import messagebox

# Настройки темы
ctk.set_appearance_mode("dark")  # Тема: dark или light
ctk.set_default_color_theme("blue") # Цветовая схема
# --- Добавляем класс для красивого окна ошибки ---
class ErrorWindow(ctk.CTkToplevel):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Ошибка")
        self.geometry("300x150")
        self.resizable(False, False)
        
        # Делаем окно поверх остальных
        self.attributes("-topmost", True)

        # Текст ошибки
        self.label = ctk.CTkLabel(self, text=message, font=("Helvetica", 14), 
                                  wraplength=250)
        self.label.pack(expand=True, padx=20, pady=20)

        # Кнопка "Ок"
        self.button = ctk.CTkButton(self, text="Понятно", fg_color="#e74c3c", 
                                    hover_color="#c0392b", width=100,
                                    command=self.destroy)
        self.button.pack(pady=(0, 20))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Calc Pro")
        
        # 1. Делаем окно шире (было 320, стало 600)
        self.geometry("600x580")
        self.resizable(False, False)

        # Контейнер для калькулятора (левая часть)
        self.calc_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calc_frame.grid(row=0, column=0, padx=10, pady=10)

        # Контейнер для истории (правая часть)
        self.history_frame = ctk.CTkFrame(self, width=250, corner_radius=10)
        self.history_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.history_label = ctk.CTkLabel(self.history_frame, text="История", font=("Helvetica", 16, "bold"))
        self.history_label.pack(pady=10)

        self.history_text = ctk.CTkTextbox(self.history_frame, width=230, height=450, font=("Helvetica", 14))
        self.history_text.pack(padx=10, pady=10)
        self.history_text.configure(state="disabled") # Запрещаем ручной ввод

        self.clear_btn = ctk.CTkButton(self.history_frame, text="Очистить историю", 
                                       fg_color="#e74c3c", hover_color="#c0392b",
                                       command=self.clear_history)
        self.clear_btn.pack(pady=10, padx=10, fill="x")

        # Поле ввода (теперь внутри calc_frame)
        self.entry = ctk.CTkEntry(self.calc_frame, width=300, height=60, font=("Helvetica", 32), 
                                  justify="right", corner_radius=10)
        self.entry.grid(row=0, column=0, columnspan=4, padx=5, pady=20)

         # Сетка 6x4: логически сгруппированная
        buttons = [
            'C', '(', ')', '/',  # Верхний ряд управления
            '7', '8', '9', '*',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '0', '.', '←', '=',  # Основной блок + удаление и результат
            '^', '√', 'π', '%'   # Дополнительные функции в самом низу
        ]

        row, col = 1, 0
        for button in buttons:
            # Цветовая логика для красоты
            if button == "=": 
                color = "#27ae60" # Зеленый (результат)
            elif button in "/*-+^√π%": 
                color = "#f39c12" # Оранжевый (операции)
            elif button == "C": 
                color = "#e74c3c" # Красный (очистка)
            elif button == "←": 
                color = "#576574" # Серый (удаление)
            elif button in "()": 
                color = "#34495e" # Темно-синий (скобки)
            else: 
                color = "#2c3e50" # Насыщенный синий (цифры и точки)

            btn = ctk.CTkButton(self.calc_frame, text=button, width=70, height=60, 
                                font=("Helvetica", 18, "bold"),
                                fg_color=color, corner_radius=12,
                                command=lambda b=button: self.on_click(b))
            btn.grid(row=row, column=col, padx=5, pady=5)
            
            col += 1
            if col > 3:
                col = 0
                row += 1


    def add_to_history(self, record):
        # Функция для добавления записи в историю
        self.history_text.configure(state="normal") # Разрешаем запись
        self.history_text.insert("end", record + "\n" + "-"*20 + "\n")
        self.history_text.configure(state="disabled") # Снова блокируем
        self.history_text.see("end") # Прокрутка вниз

    def clear_history(self):
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.configure(state="disabled")

    def on_click(self, text):
        current = self.entry.get()
        
        if text == "=":
            try:
                expr = current.strip()

                # Replace symbols
                expr = expr.replace('^', '**')
                expr = expr.replace('π', str(math.pi))
                expr = expr.replace('√', 'math.sqrt')

                # Smart percentage handling

                # Example: 100+5% -> 100+(100*5/100)
                expr = re.sub(
                    r'(\d+(\.\d+)?)([+\-])(\d+(\.\d+)?)%',
                    lambda m: f"{m.group(1)}{m.group(3)}({m.group(1)}*{m.group(4)}/100)",
                    expr
                )

                # Example: 200*10% -> 200*(10/100)
                expr = re.sub(
                    r'(\d+(\.\d+)?)([*/])(\d+(\.\d+)?)%',
                    lambda m: f"{m.group(1)}{m.group(3)}({m.group(4)}/100)",
                    expr
                )

                # Example: 50% -> (50/100)
                expr = re.sub(
                    r'(\d+(\.\d+)?)%',
                    r'(\1/100)',
                    expr
                )

                # Evaluate safely
                res = eval(expr, {"__builtins__": None, "math": math})

                # Clean integer formatting
                if res == int(res):
                    result_str = str(int(res))
                else:
                    result_str = str(round(res, 8))

                # Save history
                self.add_to_history(f"{current} = {result_str}")

                self.entry.delete(0, "end")
                self.entry.insert(0, result_str)

            except ZeroDivisionError:
                self.show_error("Нельзя делить на ноль")

            except SyntaxError:
                self.show_error("Неправильное выражение")

            except Exception:
                self.show_error("Ошибка вычисления")

        elif text == "√":
           self.entry.insert("end", "√(")
        elif text == "C":
            self.entry.delete(0, "end")
        elif text == "←":
            # Удаляем один последний символ
            self.entry.delete(len(current)-1, "end")
        else:
            self.entry.insert("end", text)

    def show_error(self, message):
        ErrorWindow(message=message)

if __name__ == "__main__":
    app = App()
    app.mainloop()

