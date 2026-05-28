from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ..core import settings
from ..services import get_group_students





class EskizSMSService:
    def __init__(self):
        self.token: Optional[str] = None
        self.base_url = 'https://notify.eskiz.uz/api'
        self.email = settings.email
        self.password = settings.password
        self.from_name = settings.from_name
        self.callback_url = settings.callback_url
    
    async def get_token(self) -> str | None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                data={
                    "email": settings.email,
                    "password": settings.password,
                }
            )
            try:
                data = response.json()
                self.token = data["data"]["token"]
                return self.token
            except Exception as e:
                pass
                self.token = None
                return None
    
    async def get_user(self) -> dict:
        if not self.token:
            token = await self.get_token()
            if not token:
                return None
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/auth/user",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            return response

    async def send_sms(self, phone: str, name: str, soat: str):
        if not self.token:
            token = await self.get_token()
            if not token:
                return None
        # message = f"Assolomu alaykum {name} ning ota-onasi. Farzandingiz bugun soat {soat} dagi darsga qatnashmadi.  Leaders Academy !!!"
        message = "Bu Eskiz dan test"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/message/sms/send",
                    headers={"Authorization": f"Bearer {self.token}"},
                    data={
                        "mobile_phone": phone,
                        "message": message,
                        "from": self.from_name,
                        "callback_url": self.callback_url
                    }
                )
                return response
        except Exception as e:
            return None

    



sms_service = EskizSMSService()


async def send_sms(session: AsyncSession, data: dict[str , str | list]):
    group_id = data.get('group_id')
    student_ids = data.get('student_ids')
    group = await get_group_students(session, group_id)
    
    students = []
    for student in group.students:
        if student.student_id in student_ids:
            students.append(student)

    for student in students:
        response = await sms_service.send_sms(
            phone=student.contact.student_parent_number,
            name=student.first_name + " " + student.last_name,
            soat=group.class_date
        ) 
        if not response:
            continue
        if response.status_code == 401:
            token = await sms_service.get_token()
            if not token:
                continue
            await sms_service.send_sms(
                phone=student.contact.student_parent_number,
                name=student.first_name + " " + student.last_name,
                soat=group.class_date
            ) 
        
        

            
