#!/usr/bin/env python
# coding: utf-8

# In[4]:


import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time

PALE_BLUE = '#add8e6'

class FipsCheckerApp:
    def __init__(self, master):
        self.master = master
        master.title("проверка названий в ФИПС по классам")
        master.geometry("600x600")
        master.configure(bg=PALE_BLUE)
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Текст для названий
        tk.Label(master, text="Варианты названий (по одному на строку):", bg=PALE_BLUE).pack(pady=(10, 0))
        self.names_text = tk.Text(master, width=50, height=10)
        self.names_text.pack(pady=5)

        # Текст для классов
        tk.Label(master, text="Номера классов (через пробел или по строкам, не более 3х):", bg=PALE_BLUE).pack(pady=(10, 0))
        self.classes_text = tk.Text(master, width=50, height=5)
        self.classes_text.pack(pady=5)

        # Кнопка запроса
        self.query_button = tk.Button(master, text="Запрос", command=self.on_query)
        self.query_button.pack(pady=20)

        self.driver = None

    def on_query(self):
        # Считываем данные из GUI
        names_raw = self.names_text.get("1.0", tk.END).strip()
        classes_raw = self.classes_text.get("1.0", tk.END).strip()
        names = [line for line in names_raw.splitlines() if line.strip()]
        classes = classes_raw.replace('\n', ' ').split()

        if not names:
            messagebox.showwarning("Внимание", "Не введено ни одного названия.")
            return
        if not classes:
            messagebox.showwarning("Внимание", "Не введён ни один класс.")
            return

        # Блокируем кнопку, чтобы исключить повторный запуск
        self.query_button.config(state=tk.DISABLED)

        # Запуск проверки в отдельном потоке
        threading.Thread(target=self.perform_search, args=(names, classes), daemon=True).start()

    def perform_search(self, names, classes):
        try:
            # Инициализация драйвера
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
            self.driver.maximize_window()

            for idx, name in enumerate(names):
                url = "https://linkmark.ru"
                if idx == 0:
                    self.driver.get(url)
                else:
                    self.driver.execute_script(f"window.open('{url}');")
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                time.sleep(3)

                # Ввод названия
                try:
                    inp = self.driver.find_element(By.CSS_SELECTOR, "input.search-input[name='search']")
                    inp.clear()
                    inp.send_keys(name)
                except:
                    continue

                # Добавить класс
                try:
                    btn = self.driver.find_element(By.CSS_SELECTOR, "a.mktu-add[data-bind='btnAdd']")
                    btn.click()
                except:
                    continue

                time.sleep(1)

                # Ввод каждого класса
                for cls in classes:
                    try:
                        cinp = self.driver.find_element(By.CSS_SELECTOR, "input.mktu-search[data-bind='mktu_search']")
                        cinp.clear()
                        cinp.send_keys(cls)
                        cinp.send_keys(Keys.RETURN)
                    except:
                        continue

                # Нажать "Найти"
                try:
                    sb = self.driver.find_element(By.CSS_SELECTOR, "button.search-bottom#search-bottom")
                    sb.click()
                except:
                    continue

                time.sleep(5)

        finally:
            # После завершения проверки — разблокировать кнопку и уведомить пользователя
            self.master.after(0, lambda: self.query_button.config(state=tk.NORMAL))
            messagebox.showinfo("Готово", "Проверка завершена")

    def on_close(self):
        # При закрытии окна — корректно закрыть Selenium и выйти
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.master.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = FipsCheckerApp(root)
    root.mainloop()


# In[ ]:




