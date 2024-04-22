from requests import get

print(get('https://worckserch.glitch.me/api/vacancies').json())
print(get('https://worckserch.glitch.me/api/users').json())
print(get('https://worckserch.glitch.me/api/vacancy/salary/from100to100000').json())
