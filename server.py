"""
Модуль простого HTTP-сервера для домашней работы №21.2.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from typing import Dict, List
import os
import threading
import time

hostName: str = "localhost"
serverPort: int = 8080
TEMPLATES_DIR: str = os.path.join(os.path.dirname(__file__), "templates")

# Глобальная переменная для управления сервером
server_instance: HTTPServer = None
should_stop: bool = False


class MyServer(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов."""

    def __read_template(self, filename: str) -> str:
        """Читает HTML-файл через контекстный менеджер."""
        filepath: str = os.path.join(TEMPLATES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    def __send_html(self, html_content: str, status: int = 200) -> None:
        """Отправляет HTTP-ответ с HTML-содержимым."""
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(html_content, "utf-8"))

    def __get_page_html(self, title: str, content: str) -> str:
        """
        Генерирует HTML-страницу с сайдбаром.

        Args:
            title: Заголовок страницы
            content: Основное содержимое

        Returns:
            Полный HTML-документ
        """
        return f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ display: flex; min-height: 100vh; }}
                .sidebar {{ width: 250px; background: #212529; color: #fff; padding: 20px; display: flex; flex-direction: column; }}
                .sidebar a {{ color: #adb5bd; text-decoration: none; padding: 10px; display: block; border-radius: 5px; margin-bottom: 5px; }}
                .sidebar a.active, .sidebar a:hover {{ background: #0d6efd; color: #fff; }}
                .sidebar .bottom-menu {{ margin-top: auto; }}
                .content {{ flex: 1; padding: 30px; }}
            </style>
        </head>
        <body>
            <nav class="sidebar">
                <h4>Меню</h4>
                <a href="/" class="{'active' if title == 'Главная' else ''}"> Главная</a>
                <a href="/category" class="{'active' if 'Категория' in title else ''}">📁 Категории</a>
                <a href="/orders" class="{'active' if 'Заказы' in title else ''}">📦 Заказы</a>
                <a href="/contacts" class="{'active' if 'Контакты' in title else ''}">📞 Контакты</a>
                <div class="bottom-menu">
                    <div class="dropdown">
                        <button class="btn btn-dark dropdown-toggle w-100 text-start" type="button" data-bs-toggle="dropdown">
                            👤 Пользователь
                        </button>
                        <ul class="dropdown-menu dropdown-menu-dark">
                            <li><a class="dropdown-item" href="/profile">Профиль</a></li>
                            <li><a class="dropdown-item" href="/logout">Выход</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
            <main class="content">
                {content}
            </main>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """

    def do_GET(self) -> None:
        """Обрабатывает GET-запросы."""
        global should_stop
        parsed_path = urlparse(self.path)
        path: str = parsed_path.path

        # Главная страница
        if path == "/" or path == "/index":
            content = """
            <h1 class="text-center">Главная</h1>
            <p class="text-center text-muted">Вы находитесь на сайте, предназначенном для продажи товаров.</p>
            <div class="row">
                <div class="col-md-4"><div class="card"><div class="card-body"><h5 class="card-title">Товар 1</h5><h3>$ 100</h3><p class="card-text">10 users included, 2 GB of storage</p><button class="btn btn-outline-primary w-100">Купить</button></div></div></div>
                <div class="col-md-4"><div class="card"><div class="card-body"><h5 class="card-title">Товар 2</h5><h3>$ 100</h3><p class="card-text">10 users included, 2 GB of storage</p><button class="btn btn-outline-primary w-100">Купить</button></div></div></div>
                <div class="col-md-4"><div class="card"><div class="card-body"><h5 class="card-title">Товар 3</h5><h3>$ 100</h3><p class="card-text">10 users included, 2 GB of storage</p><button class="btn btn-outline-primary w-100">Купить</button></div></div></div>
            </div>
            """
            self.__send_html(self.__get_page_html("Главная", content))

        # Страница категории
        elif path == "/category":
            cards = ""
            for i in range(1, 7):
                cards += f"""
                <div class="col-md-4 mb-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h5 class="card-title">Товар {i}</h5>
                            <h3>$ 100</h3>
                            <p class="card-text">10 users included, 2 GB of storage, Email support</p>
                            <button class="btn btn-outline-primary w-100">Купить</button>
                        </div>
                    </div>
                </div>
                """
            content = f"<h1 class=\"text-center\">Категория 1</h1><div class=\"row mt-4\">{cards}</div>"
            self.__send_html(self.__get_page_html("Категория 1", content))

        # Страница заказов
        elif path == "/orders":
            content = """
            <h1 class="text-center">Заказы</h1>
            <div class="alert alert-info mt-4">
                <h4>У вас пока нет заказов</h4>
                <p>Перейдите в каталог товаров, чтобы сделать первый заказ.</p>
                <a href="/category" class="btn btn-primary">Перейти к покупкам</a>
            </div>
            """
            self.__send_html(self.__get_page_html("Заказы", content))

        # Страница контактов
        elif path == "/contacts":
            content = """
            <h1 class="text-center mb-4">Контакты</h1>
            <div class="row">
                <div class="col-md-6">
                    <form method="POST" action="/contacts">
                        <div class="mb-3">
                            <label class="form-label">Имя</label>
                            <input type="text" name="name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Почта</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Сообщение</label>
                            <textarea name="message" class="form-control" rows="4" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Отправить</button>
                    </form>
                </div>
                <div class="col-md-6">
                    <h4>Наши контакты</h4>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                </div>
            </div>
            """
            self.__send_html(self.__get_page_html("Контакты", content))

        # Страница профиля
        elif path == "/profile":
            content = """
            <h1 class="text-center">Профиль пользователя</h1>
            <div class="card mt-4" style="max-width: 500px; margin: 2rem auto;">
                <div class="card-body">
                    <h5 class="card-title">👤 Пользователь</h5>
                    <p class="card-text">Email: user@example.com</p>
                    <p class="card-text">Роль: Покупатель</p>
                    <button class="btn btn-outline-primary">Редактировать профиль</button>
                </div>
            </div>
            """
            self.__send_html(self.__get_page_html("Профиль", content))

        # ВЫХОД ИЗ СИСТЕМЫ - остановка сервера и закрытие вкладки
        elif path == "/logout":
            # Устанавливаем флаг остановки
            should_stop = True

            # Возвращаем страницу с JavaScript для закрытия вкладки
            logout_html = """
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Выход</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body class="text-center py-5 bg-light">
                <div class="container">
                    <div class="alert alert-success mt-5">
                        <h2>👋 Вы успешно вышли из системы</h2>
                        <p>Сервер остановлен. Вкладка закроется автоматически...</p>
                    </div>
                </div>
                <script>
                    // Закрываем вкладку браузера
                    window.close();
                    // Если window.close() не сработал (политика безопасности браузера)
                    // показываем сообщение и предлагаем закрыть вручную
                    setTimeout(function() {
                        alert('Пожалуйста, закройте вкладку вручную.');
                    }, 1000);
                </script>
            </body>
            </html>
            """
            self.__send_html(logout_html)

            # Останавливаем сервер в отдельном потоке через небольшую задержку
            def stop_server():
                global server_instance
                time.sleep(0.5)  # Даём время на отправку ответа
                if server_instance:
                    print("\n🛑 Остановка сервера...")
                    server_instance.shutdown()

            threading.Thread(target=stop_server, daemon=True).start()

        # Страница 404
        else:
            content = """
            <div class="text-center py-5">
                <h1>404</h1>
                <p class="lead">Страница не найдена</p>
                <a href="/" class="btn btn-primary">На главную</a>
            </div>
            """
            self.__send_html(self.__get_page_html("404", content), status=404)

    def do_POST(self) -> None:
        """Обрабатывает POST-запросы."""
        parsed_path = urlparse(self.path)
        path: str = parsed_path.path

        if path == "/contacts":
            content_length: int = int(self.headers.get("Content-Length", 0))
            raw_data: str = self.rfile.read(content_length).decode("utf-8")
            form_data: Dict[str, List[str]] = parse_qs(raw_data)

            print("=" * 50)
            print(" Получен POST-запрос на /contacts")
            print("📋 Данные от пользователя:")
            for key, values in form_data.items():
                print(f"   {key}: {values[0]}")
            print("=" * 50)

            content = """
            <h1 class="text-center mb-4">Контакты</h1>
            <div class="alert alert-success">✅ Сообщение успешно отправлено!</div>
            <div class="row">
                <div class="col-md-6">
                    <form method="POST" action="/contacts">
                        <div class="mb-3">
                            <label class="form-label">Имя</label>
                            <input type="text" name="name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Почта</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Сообщение</label>
                            <textarea name="message" class="form-control" rows="4" required></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary">Отправить</button>
                    </form>
                </div>
                <div class="col-md-6">
                    <h4>Наши контакты</h4>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                </div>
            </div>
            """
            self.__send_html(self.__get_page_html("Контакты", content))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("<h1>404 Not Found</h1>", "utf-8"))


if __name__ == "__main__":
    server_instance = HTTPServer((hostName, serverPort), MyServer)
    print(f"🚀 Сервер запущен: http://{hostName}:{serverPort}")
    print("📄 Открой в браузере: http://localhost:8080")
    print("💡 Для выхода из системы перейди на: http://localhost:8080/logout")

    try:
        server_instance.serve_forever()
    except KeyboardInterrupt:
        print("\n⚠️  Остановка сервера (Ctrl+C)...")
    finally:
        server_instance.server_close()
        print("🛑 Сервер остановлен.")
