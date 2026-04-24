from sqlalchemy import Column, Integer, Text, String
from database import Base;

class AgentReportModel(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    key_points = Column(Text)
    sentiment = Column(String)
    token_usage_saved = Column(Integer)



