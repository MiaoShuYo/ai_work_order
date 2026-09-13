from pydantic import BaseModel, Field

class LogisticsStep(BaseModel):
    """
    物流轨迹里的一个节点，节点之间用 time 排序就是完整的运输过程。
    """

    time: str = Field(description="节点时间，格式 yyyy-MM-dd HH:mm:ss")
    location: str = Field(description="节点所在地点，例如 杭州转运中心")
    description: str = Field(description="节点动作描述，例如 快件已到达【杭州转运中心】")

class LogisticsInfo(BaseModel):
    """
    某个订单的物流轨迹明细，steps 按时间正序排列。
    """

    order_no: str = Field(description="订单号")
    steps: list[LogisticsStep] = Field(description="轨迹节点列表，按时间从早到晚")

