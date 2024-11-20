
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class input_UrlText:
    def __init__(self, url):
        self.url = url
        self.article_info = {
            'id': "0",
            'title': "null",
            'author': "null",
            'date': "null",
            'content': "null"
        }

    def get_Text_in_Url(self):
        try:
            # Gửi yêu cầu đến URL
            response = requests.get(self.url)

            # Kiểm tra mã trạng thái của yêu cầu
            if response.status_code != 200:
                self.article_info['content'] = f"Error: {response.status_code}"
                return self.article_info 

            # Phân tích cú pháp HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Lấy tiêu đề bài báo
            self.article_info['title'] = soup.find('h1').text.strip() if soup.find('h1') else "null"

            # Lấy tác giả
            author_candidates = [
                soup.find('span', class_='byline'),
                soup.find('meta', attrs={'name': 'author'}),
                soup.find('meta', attrs={'property': 'article:author'})
            ]
            for candidate in author_candidates:
                if candidate:
                    self.article_info['author'] = candidate.get('content', candidate.text.strip())
                    break

            # Lấy ngày tháng
            date_candidates = [
                soup.find('time'),
                soup.find('meta', property='article:published_time'),
                soup.find('meta', attrs={'name': 'date'}),
                soup.find('meta', attrs={'name': 'pubdate'})
            ]
            for candidate in date_candidates:
                if candidate:
                    date_value = candidate.get('datetime', candidate.get('content', "null"))
                    if date_value != "null":
                        self.article_info['date'] = self.parse_date(date_value)
                        if self.article_info['date'] != "null":
                            break

            # Lấy nội dung bài báo
            content = (
                soup.find('div', class_='article-body') or
                soup.find('div', class_='content') or
                soup.find('article')
            )
            self.article_info['content'] = content.text.strip() if content else "null"

            # Đặt id là "1" nếu thành công
            self.article_info['id'] = "1"

            return self.article_info

        except requests.exceptions.RequestException as e:
            self.article_info['content'] = f"Error: {str(e)}"
            return self.article_info

    @staticmethod
    def parse_date(date_string):
        # Danh sách các định dạng ngày tháng cần xử lý
        date_formats = [
            "%B %d, %Y",  # Ví dụ: October 9, 2024
            "%d %B %Y",   # Ví dụ: 9 October 2024
            "%d.%m.%Y",   # Ví dụ: 09.10.2024
            "%d/%m/%Y",   # Ví dụ: 09/10/2024
            "%Y-%m-%d",   # Ví dụ: 2024-10-09 (theo chuẩn ISO)
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_string, fmt).strftime("%d/%m/%Y")
            except ValueError:
                continue  # Nếu không khớp định dạng, thử định dạng tiếp theo
        return "null"  # Trả về "null" nếu không thể phân tích ngày
