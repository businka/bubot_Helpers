##Сообщение содержащие информацию о вызываемом действии
* uid - уникальный идентификатор экземпляра действия
* type - actionCall
* name - идентификатор действия
* data - словарь с параметрами действия

----
Добавляется исполнителем действия
* executor - исполнитель действия
* notificator - объект реализующий уведомления
* arrival - время поступления
* begin - начало выполнения
* end - конец выполнения
* stat - статистика действия, отражаются все вложенные действия 
* session
  * uid
  * user
  * account

##Сообщение содержащие результат выполнения действия
* uid - уникальный идентификатор экземпляра действия
* type - actionResult
* name - идентификатор действия
* data - идентификатор действия
* stat - возвращается только в отладочном режиме

##Сообщение содержащие уведомления о ходе  выполнения действия
* uid - уникальный идентификатор экземпляра действия
* type - actionNotify
* name - идентификатор действия
* data - идентификатор действия

##Сообщение содержащие комманду отмены действия
* uid - уникальный идентификатор экземпляра действия
* type - actionCancel
* name - идентификатор действия

##Сообщение содержащие данные ошибки выполнения действия
* uid - уникальный идентификатор экземпляра действия
* type - actionError
* name - идентификатор действия
* data - данные ошибки
