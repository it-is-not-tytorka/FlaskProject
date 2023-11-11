# Документация  
Данное API реализовано с помощью библиотеки Flask. Программа реализует функционал облачного хранения фотографий. Пользователь программы может создавать свои папки, в которых будут храниться фотографии. К фотографиям можно добавлять комментарии. Также есть возможность для того, чтобы делиться с другими пользователями доступом к папке, настраивать их возможности изменения фотографий. Так, в папке могут быть пользователи с доступом только для просмотра и комментирования фотографий или модераторы, которые могут удалять любые комментарии, фотографии или добавлять новые. На данный момент программа работает в рантайме и не запомниает пользователей и их данные. Все пользователи находятся в глобальной переменной USERS.


# Как работают роуты?
В папке `/app/views ` есть файлы `.py`, в которых реализована логика роутов. Каждый файл имет название того объекта, с которым взаимодействует. Если запрос успешно прошел, то программа выдает HTTP статус 200 и ответ в стиле json или статус 204, если передавать в ответ нечего. В случаях неудачного запроса программа отлавливает ошибку и выдает статус 400 или 404 и информацию об ошибке в стиле json. Ниже приведены примеры роутов.


## USERS 
### `POST /user/create`  
Создание пользователя. В ответе выводится вся информация о новом пользователе. ID пользователя гинерируется на основе длины словаря USERS.  
Request example:
```json
{
    "first_name": "string",
    "last_name": "string",
    "phone": "number",
    "email": "string"
}
```
Responce example:
```json
{
    "first_name": "string",
    "last_name": "string",
    "phone": "number",
    "email": "string",
    "id": int,
    "folder_count": 0,
    "image_count": 0,
    "comment_count": 0,
    "folders": []
}
```

### `GET /user/<int:user_id>/info`  
Получение всей информации о существующем пользователе.   
Responce example:
```json
{
    "first_name": "string",
    "last_name": "string",
    "phone": "number",
    "email": "string",
    "id": int,
    "folder_count": int,
    "image_count": int,
    "comment_count": int,
    "folders": [
        {
            "folder_id": "string",
            "name": "string",
            "folder_users": {
                "int": "owner",
                ...
            },
            "images": [
                {
                    "image_id": "string",
                    "title": "string",
                    "user_id": int,
                    "path": "string",
                    "comments": [
                        {
                            "comment_id": "srting",
                            "comment_text": "string",
                            "user_id": int,
                            "date": "string"
                        },
                        ...
                    ]
                },
                ...
            ]
        }
    ]
}
```

### `GET /user/<int:user_id>/stats`   
Генерируется график с помощью библиотеки Matplotlib, который показывает, сколько папок и фотографий пользователь создал, сколько комментариев осталось. В колонке с папками будет отображаться велечина, которая означает количество всех папок, к которым пользователь имеет доступ даже если он не является создателем каких-то из них. В колонке с фотографиями и комментариями будет отображаться величина, которая означает количество объектов, которые создал пользователь и которые не были удалены. То есть может получиться так, что у пользователя отменили доступ к папке, в которой он оставлял комментарии. Если эти комментарии не удалены, то они все равно считаются, даже если он не имеет к ним доступа.  
Responce example:
```html
<img src="link">
```

### `DELETE /user/<int:user_id>/delete`   
Удаление пользователя. Атрибут `status` пользователя помечается как `deleted`, после чего о нем нельзя получить новую инфомрацию, удаляются все папки, в которых 
Responce example:
```html
<img src="link">
```

## FOLDERS
### `POST user/<int:user_id>/folders/create`   
Создание новой папки.  
Request example:
```json
{
    "folder_name": "string"
}
```
Responce example:
```json
{
    "folder_id": "string"
}
```

### `GET /user/<int:user_id>/folders/swap`
Две папки меняются местами у пользователя. Может потребоваться для дальнейшего отображения папок, чтобы какая-то была показана выше на странице, какая-то ниже.   
Request example:
```json
{
    "first_folder_id": "string",
    "second_folder_id": "string"
}
```

### `DELETE /user/<int:user_id>/folders/delete`   
Удаление папки. Если пользователь не является создателем папки, то он удалит папку только у себя. Если пользователь - создатель папки, то изменится количество фотографий и комментариев у пользователей, который имели доступ к этой папке и создавали объекты в ней, так как в этом случае объекты удалятся безвозвратно. После удаления папки создателем остальные пользователи, которые имели доступ, будут видеть информацию в `GET /user/<int:user_id>/info`, что папка была удалена создателем.  
Request example:
```json
{
    "folder_id": "string"
}
```

### `GET /user/<int:user_id>/folders/share`   
Если пользователь имеет права для того, чтобы делиться папкой, то у пользователя с ID `user_to_receive_id` появится новая папка с ID `shared_folder_id` и со всем контентом, который в ней был. Параметр `access_edit` влияет на возможность пользователя `user_to_receive` изменять контент внутри папки.  
Request example:
```json
{
    "user_to_receive_id": int,
    "shared_folder_id": "string",
    "access_edit": "bool"
}
```
### `GET /user/<int:user_id>/folders/unshare`   
Отменять доступ может только создатель папки. У пользователя с ID `user_to_unshare_id` пропадет папка из атрибута `folders`.  
Request example:
```json
{
    "folder_id": "string",
    "user_to_unshare_id": 0
}
```

## IMAGES
### `POST /user/<int:user_id>/images/create`   
Создание фотографии в папке. Параметр `path` содержит url ссылку на изображение. В дальнейшем параметр можно изменить, чтобы он содержал объект из базы данных, в которой хранятся все фотографии.  
Request example:
```json
{
    "folder_id":"string",
    "title": "string",
    "path": "string"
}
```
Responce example:
```json
{
    "folder_id": "string",
    "image_id": "string"
}
```

### `GET /user/<int:user_id>/images/swap`   
Изменение порядка двух фотографий в папке. Изменять порядок может пользователь с любым уровнем доступа к папке, потому что изменения будет видеть только он.  
Request example:
```json
{
    "folder_id": "string",
    "first_image_id": "string",
    "second_image_id": "string"
}
```

### `DELETE /user/<int:user_id>/images/delete`   
Если пользователь имеет доступ к удалению фотографий, то объект безвозратно исчезнет, после чего произойдет пересчет `comment_count` у пользователей, которые оставляли комментарии под этой фотографией. У автора изображения `image_count` уменьшится на 1.  
Request example:
```json
{
    "folder_id": "string",
    "image_id": "string"
}
```

## COMMENTS
### `POST /user/<int:user_id>/comments/add`   
Создание комментария под фотографией. Атрибут `comment_count` у пользователя, который оставил комментарий увеличивается на 1.  
Request example:
```json
{
    "folder_id": "string",
    "image_id": "string",
    "comment_text": "string"
}
```
Responce example:
```json
{
    "folder_id": "string",
    "image_id": "string",
    "comment_id": "string"
}
```

### `DELETE /user/<int:user_id>/comments/delete` 
Удаление комментария. Атрибут `comment_count` у создателя комментария уменьшится на 1.    
Request example:
```json
{
    "folder_id": "string",
    "image_id": "string",
    "comment_id": "string"
}
```

# Классы
## User
### ```__init__(self, first_name : str, last_name : str, phone : str, email : str, id : int)```  
Создание экземпляра. Атрибут `folders` представляет из себя словарь, в котором в качестве ключей выступают ID папок, в качестве значений выступают экземпляры класса `Folder`, к которым у пользователя есть доступ. Либо он создал их сам, либо получил доступ к ним от другого пользователя. Атрибут `image_count` - количество фотографий, которые создал пользователь, но которые не были удалены. Возможен случай, когда пользователь создал фотографию в папке, к которой у него был доступ, но потом этот доступ забрали. Тогда пользователь не имеет доступ к своей фотографии, но при этом счетчик отоброжает, что эта фотография у него есть. В случае, если сам пользователь или другой пользователь с правами удалил фотографию, счетчик уменьшается. Атрибут `comment_count` аналогичен `image_count`.
### ```get_info(self)```
Метод представляет всю информацию о пользователе в виде словаря для роута `POST /user/create`  и `GET /user/<int:user_id>/info`. Для ключа `folders`, чтобы получить из экземпляров класса `Folder` информацию в виде словаря, применяется метод `folder.to_dict()`.
### ```folder_count(self)```
Геттер, который выводит количество папок у пользователя, к которым он имеет доступ. Лямбда функция проверяет, что папка была не удалена, в противном случае количество не будет увеличено.
### ```is_valid_phone(phone_numb : str)```
Валидация телефона с помощью библиотеки re.
### ```is_valid_email(email : str)```
Валидация почты с помощью библиотеки re.
### ```is_unique_params(data : dict, *args)```
Проверка, что пользователь обладает уникальными параметрами, которые передаются в *args.
### ```is_valid_user_id(user_id: int)```
Валидация ID пользователя.
### ```share_folder(user_to_receive, folder)```
В словарь `folders` пользователя с ID `user_to_receive` добавляется экземпляр класса `Folder`.
### ```delete_folder(self, folder_id)```
Удаление объекта из словаря `folders` у пользователя. Дополнительная проверка, что папка была созадана этим пользователем, потому что только после его удаления информация о папке пропадет у всех пользователей, которые имеют к ней доступ. Если папка была добавлена пользователю через метод `share_folder` другого пользователя, то после удаления информация исчезнет только у одного пользователя, который удалил папку.

## Folder
### ```__init__(self, id: str, name: str, owner_id: int)```
Создание пользователем новой папки, владельцем которой он является. Атрибут `access_edit` - доступ для изменения содержания папки. Если `access_edit = True`, то пользователь имеет доступ для удаления и создания фотографий в папке, удаления комментариев других пользователей, добавления новых пользователей в папку, но при этом удалять старых пользователей может только пользователь с доступом `owner`. Пользователи с `access_edit = False` могут только смотреть фотографии, комментировать их и удалять только свои комментарии. Атрибут `is_deleted` указывает, была ли удалена папка или нет. В случаях, если `is_deleted = True`, изменяется логика метода `to_dict` и при попытке изменения содержания в такой папке Response будет выдавать ошибку 400.
Атрибут `images` является словарем, подобному `folders` у пользователя. В ключах содержатся ID изображений, а в значениях - экземпляры класса `Image`. Атрибут `users` является словарем, в котором ключи - ID пользователей, а значения - уровень доступа для изменений папки. Доступ `owner` есть только у создателя папки. Доступ `moderator` у пользователей, которые имеют доступ к папки и у них атрибут `access_edit = True`, пользователи с `access_edit = False` получают доступ `reader`.

### ```create_folder(self, user: User)```
Метод, который добавляет в словарь `folders` у пользователя созданную папку.

### ```is_valid_folder_id(user_id : int, folder_id : str)```
Валидация пользоваелся и проверка, что у него есть доступ к папке.

### ```to_dict(self)```
Возвращает информацию о папке и вызывает метод `to_dict` у экземпляров класса `Images`, которые находятся в папке. В случае, если папка была удалена возвращается ошибка в стиле json:
```json
{
    "folder_id": "string",
    "error": "The folder was deleted by it's owner."
}
```

### ```create_image(self, image : Image)```
Добавление экземпляра класса `Image` в словарь `images` у папки.

### ```create_image(self, image : Image)```
Удаление изображения из словаря `images`.

### ```is_able_to_edit_images(self)```
Проверяет атрибут `access_edit`, который есть у папки, чтобы определить, может ли пользователь изменять контент внутри.

## SharedFolder(Folder)
### ```_init_```
Дочерний класс класса `Folder`. Атрибуты копируют данные папки, к которой пользователь получил доступ. Новый атрибут `main_folder` - ссылка на оригинальную папку. Проверка параметра `access_edit`, чтобы определить права пользователя и назначить его как `moderator` или `reader`.

### ```is_deleted(self)```
Геттер атрибута `is_deleted`, который возвращает атрибут `is_delted` оригинальной папки. Если оригинальная папка была удалена создателем, то геттер вернет `False`. В других случаях папка не будет помечена, как удаленная.

### ```create_image(self, image)```
Если пользователь имеет доступ для создания фотографий, то фотография должна быть создана в оригинальной папке, чтобы все остальные пользователи могли ее видеть.

## Image
### ```__init__(self, id: str, path: str, title: str, user_id: int)```
Создание экземпляра. Атрибут `path` содержит url ссылку на изображение. Атрибут `comments` является словарем, в котором ключами являются ID комментариев, а значениями - сами экзмепляры класса `Comment`. Атрибут `user_id` - ID создателя изображения.

### ```is_valid_image_id(folder: Folder, image_id: int)```
Валидация ID изображения. ID должен быть строкой и содержаться в ключах словаря `images` папки, которая была передана в метод.

### ```add_comment(self, comment : Comment)```
Добавление комментария под изображение. В словарь `comments` добавляется новый объект класса `Comment`

### ```delete_comment(self, comment_id: str)```
Удаление комментария из словаря `comments` изображения.

### ```to_dict(self)```
Представляет всю информацию о фотографии в виде словаря. У экземпляров класса `Comment` вызывается метод `to_dict`, чтобы их данные были тоже в виде словаря.

## Comment
### ```__init__(self, text : str, id : str, user_id : int, date : str)```
Создание экземпляра. Атрибут `text` - содержание комментария, `user_id` - ID пользователя, который оставил комментарий, `date` - дата, когда комментарий был создан.

### ```is_valid_comment_id(image : Image, comment_id : str)```
Валидация ID комментария. Проверка, что ID является строкой и содержится в комментариях `comments` изображения, которое было передано в метод.

### ```to_dict(self)```
Возвращает словарь, в котором представлена вся информация о комментарии.

## Editor
### ```def swap_elements(first_el_id: int, second_el_id: int, old_dict: dict)```
Меняет два элемента с ID `first_el_id` и `second_el_id` местами в словаре `old_dict`. Метод возвращает новый словарь, в котором элементы с этими ID находятся в другом порядке. В случае, если элементов с такими ID нет, метод возращает `None`.

### ```recalculate_counts_folder(folder : Folder)```
Если папка будет окончательно удалена для всех пользователей, например, самим создаетелем, то автоматически удаляется вся информация о фотографиях и комментариях, которые находятся внутри папки. После этого должно уменьшиться количество фотографий `image_count` и комментариев `comment_count`, у пользователей, которые их оставили. Для каждого изображения в папке `folder` применяет метод ```recalculate_counts_image```

### ```recalculate_counts_image(image : Image)``` 
Если изображение окончательно удаляется, то у его создателя с ID `user_id` уменьшается количество фотографий `image_count` на 1. Для всех комментариев под фотографией применяется метод ```recalculate_counts_comment```.

### ```recalculate_counts_comment(comment : Comment)```
Если комментарий окончательно удаляется, то количество комментариев `comment_count` у пользователя, который этот комментарий оставил, уменьшается.
    
### ```increase_image_count(user)```
Увеличение количества фотографий у пользователя.

### ```decrease_image_count(user)```
Уменьшение количества фотографий у пользователя.

### ```increase_comment_count(user)```
Увеличение количества комментариев у пользователя.

### ```decrease_comment_count(user)```
Уменьшение количества комментариев у пользователя.