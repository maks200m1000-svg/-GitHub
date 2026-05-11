import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
import webbrowser


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()

        self.setup_ui()

    def setup_ui(self):
        search_frame = ttk.Frame(self.root, padding="10")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        ttk.Label(search_frame, text="Поиск пользователя GitHub:").grid(row=0, column=0, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_user())

        self.search_button = ttk.Button(search_frame, text="Найти", command=self.search_user)
        self.search_button.grid(row=0, column=2, padx=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Результаты поиска")

        self.results_listbox = tk.Listbox(self.search_tab, height=15, font=("Arial", 10))
        self.results_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.results_listbox.bind("<<ListboxSelect>>", self.on_result_select)

        results_btn_frame = ttk.Frame(self.search_tab)
        results_btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(results_btn_frame, text="Добавить в избранное",
                  command=self.add_to_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(results_btn_frame, text="Показать профиль",
                  command=self.show_profile).pack(side=tk.LEFT, padx=5)

        self.favorites_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.favorites_tab, text="Избранное")

        self.favorites_listbox = tk.Listbox(self.favorites_tab, height=15, font=("Arial", 10))
        self.favorites_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.favorites_listbox.bind("<<ListboxSelect>>", self.on_favorite_select)

        fav_btn_frame = ttk.Frame(self.favorites_tab)
        fav_btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(fav_btn_frame, text="Удалить из избранного",
                  command=self.remove_from_favorites).pack(side=tk.LEFT, padx=5)
        ttk.Button(fav_btn_frame, text="Показать профиль",
                  command=self.show_favorite_profile).pack(side=tk.LEFT, padx=5)
        ttk.Button(fav_btn_frame, text="Обновить",
                  command=self.refresh_favorites_list).pack(side=tk.LEFT, padx=5)

        info_frame = ttk.LabelFrame(self.root, text="Информация о пользователе", padding="10")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)

        self.user_info_text = tk.Text(info_frame, height=10, wrap=tk.WORD)
        self.user_info_text.pack(fill=tk.BOTH, expand=True)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.current_results = []
        self.current_selected_user = None

        self.refresh_favorites_list()

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_favorites(self):
        with open(self.favorites_file, 'w', encoding='utf-8') as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)

    def search_user(self):
        username = self.search_entry.get().strip()

        if not username:
            messagebox.showwarning("Предупреждение", "Поле поиска не может быть пустым!")
            return

        self.results_listbox.delete(0, tk.END)
        self.user_info_text.delete(1.0, tk.END)

        try:
            url = f"https://api.github.com/search/users?q={username}&per_page=20"
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
            users = data.get('items', [])

            if not users:
                messagebox.showinfo("Информация", "Пользователи не найдены")
                return

            self.current_results = []
            for user in users:
                login = user['login']
                self.results_listbox.insert(tk.END, login)
                self.current_results.append(user)

            messagebox.showinfo("Успех", f"Найдено пользователей: {len(users)}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка", f"Ошибка при запросе к API: {str(e)}")

    def on_result_select(self, event):
        selection = self.results_listbox.curselection()
        if selection:
            index = selection[0]
            user = self.current_results[index]
            self.current_selected_user = user
            self.display_user_info(user)

    def on_favorite_select(self, event):
        selection = self.favorites_listbox.curselection()
        if selection:
            index = selection[0]
            user = self.favorites[index]
            self.display_user_info(user)

    def display_user_info(self, user):
        self.user_info_text.delete(1.0, tk.END)

        info = f"""
╔══════════════════════════════════════════════════════════╗
║                    ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ              ║
╠══════════════════════════════════════════════════════════╣
║ Логин: {user.get('login', 'N/A')}
║ ID: {user.get('id', 'N/A')}
║ 
║ Ссылка на профиль: {user.get('html_url', 'N/A')}
║ 
║ Тип: {user.get('type', 'N/A')}
║ 
║ API URL: {user.get('url', 'N/A')}
╚══════════════════════════════════════════════════════════╝
        """
        self.user_info_text.insert(1.0, info)

    def add_to_favorites(self):
        if not self.current_selected_user:
            messagebox.showwarning("Предупреждение", "Сначала выберите пользователя из результатов поиска")
            return

        username = self.current_selected_user['login']

        for fav in self.favorites:
            if fav['login'] == username:
                messagebox.showinfo("Информация", f"Пользователь {username} уже в избранном")
                return

        self.favorites.append(self.current_selected_user)
        self.save_favorites()
        self.refresh_favorites_list()
        messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное")

    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Сначала выберите пользователя из избранного")
            return

        index = selection[0]
        username = self.favorites[index]['login']

        if messagebox.askyesno("Подтверждение", f"Удалить {username} из избранного?"):
            del self.favorites[index]
            self.save_favorites()
            self.refresh_favorites_list()
            self.user_info_text.delete(1.0, tk.END)
            messagebox.showinfo("Успех", f"Пользователь {username} удалён из избранного")

    def refresh_favorites_list(self):
        self.favorites_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.favorites_listbox.insert(tk.END, user['login'])

    def show_profile(self):
        if not self.current_selected_user:
            messagebox.showwarning("Предупреждение", "Сначала выберите пользователя")
            return

        webbrowser.open(self.current_selected_user['html_url'])

    def show_favorite_profile(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Сначала выберите пользователя")
            return

        index = selection[0]
        webbrowser.open(self.favorites[index]['html_url'])


def main():
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()


if __name__ == "__main__":
    main()