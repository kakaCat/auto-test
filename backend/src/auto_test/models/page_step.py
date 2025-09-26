"""
页面分步保存数据模型
Page Step Save Data Models
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class PageBasicInfo(BaseModel):
    """页面基本信息模型"""
    name: str = Field(..., description="页面名称", max_length=100)
    description: Optional[str] = Field(None, description="页面描述")
    route_path: Optional[str] = Field(None, description="路由路径", max_length=200)
    page_type: str = Field("page", description="页面类型：page, modal, drawer等")
    system_id: int = Field(..., description="所属系统ID")
    module_id: Optional[int] = Field(None, description="所属模块ID")
    enabled: bool = Field(True, description="是否启用")
    icon: Optional[str] = Field(None, description="页面图标")
    permissions: Optional[List[str]] = Field(None, description="权限设置")


class ComponentConfig(BaseModel):
    """组件配置模型"""
    id: str = Field(..., description="组件ID")
    type: str = Field(..., description="组件类型")
    props: Dict[str, Any] = Field(default_factory=dict, description="组件属性")
    style: Dict[str, Any] = Field(default_factory=dict, description="样式配置")
    position: Dict[str, Any] = Field(default_factory=dict, description="位置信息")
    children: Optional[List['ComponentConfig']] = Field(None, description="子组件")


class GridConfig(BaseModel):
    """网格配置模型"""
    columns: int = Field(12, description="网格列数")
    gap: int = Field(16, description="网格间距")
    responsive: bool = Field(True, description="是否响应式")


class ThemeConfig(BaseModel):
    """主题配置模型"""
    primary_color: str = Field("#409EFF", description="主色调")
    background_color: str = Field("#FFFFFF", description="背景色")
    text_color: str = Field("#303133", description="文字颜色")


class PageLayout(BaseModel):
    """页面布局模型"""
    components: List[ComponentConfig] = Field(default_factory=list, description="组件配置列表")
    layout_type: str = Field("grid", description="布局类型")
    responsive: bool = Field(True, description="是否响应式")
    grid_config: Optional[GridConfig] = Field(None, description="网格配置")
    theme: Optional[ThemeConfig] = Field(None, description="主题配置")


class ApiConfigItem(BaseModel):
    """API配置项模型"""
    api_id: int = Field(..., description="API ID")
    execution_type: str = Field("parallel", description="执行类型: serial, parallel, conditional")
    order: int = Field(0, description="执行顺序")
    params_mapping: Optional[Dict[str, Any]] = Field(None, description="参数映射")
    response_handling: Optional[Dict[str, Any]] = Field(None, description="响应处理")
    enabled: bool = Field(True, description="是否启用")


class PageApiConfig(BaseModel):
    """页面API配置模型"""
    system_id: int = Field(..., description="系统ID")
    module_id: int = Field(..., description="模块ID")
    apis: List[ApiConfigItem] = Field(default_factory=list, description="API配置列表")


class EventTrigger(BaseModel):
    """事件触发器模型"""
    type: str = Field(..., description="触发类型")
    target: str = Field(..., description="触发目标")
    condition: Optional[Dict[str, Any]] = Field(None, description="触发条件")


class EventAction(BaseModel):
    """事件动作模型"""
    type: str = Field(..., description="动作类型")
    target: str = Field(..., description="动作目标")
    params: Optional[Dict[str, Any]] = Field(None, description="动作参数")


class InteractionEvent(BaseModel):
    """交互事件模型"""
    id: str = Field(..., description="事件ID")
    trigger: EventTrigger = Field(..., description="触发条件")
    actions: List[EventAction] = Field(default_factory=list, description="执行动作")
    enabled: bool = Field(True, description="是否启用")


class WorkflowConfig(BaseModel):
    """工作流配置模型"""
    id: str = Field(..., description="工作流ID")
    name: str = Field(..., description="工作流名称")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="工作流步骤")
    enabled: bool = Field(True, description="是否启用")


class PageInteraction(BaseModel):
    """页面交互模型"""
    events: List[InteractionEvent] = Field(default_factory=list, description="交互事件列表")
    workflows: List[WorkflowConfig] = Field(default_factory=list, description="工作流配置")


StepStatus = Literal['pending', 'draft', 'completed']


class PageProgress(BaseModel):
    """页面配置进度模型"""
    page_id: int = Field(..., description="页面ID")
    current_step: int = Field(0, description="当前步骤")
    completed_steps: List[int] = Field(default_factory=list, description="已完成步骤")
    step_status: Dict[str, StepStatus] = Field(
        default_factory=lambda: {
            'basic': 'pending',
            'layout': 'pending',
            'api': 'pending',
            'interaction': 'pending'
        },
        description="步骤状态"
    )
    last_saved_at: datetime = Field(default_factory=datetime.now, description="最后保存时间")
    is_completed: bool = Field(False, description="是否完成配置")


class PageStepSaveRequest(BaseModel):
    """页面步骤保存请求模型"""
    step_data: Dict[str, Any] = Field(..., description="步骤数据")


class PageStepSaveResponse(BaseModel):
    """页面步骤保存响应模型"""
    page_id: int = Field(..., description="页面ID")
    step: str = Field(..., description="保存的步骤")
    status: StepStatus = Field(..., description="保存状态")
    saved_at: datetime = Field(..., description="保存时间")


class PageCompleteRequest(BaseModel):
    """页面配置完成请求模型"""
    pass


class PageCompleteResponse(BaseModel):
    """页面配置完成响应模型"""
    page_id: int = Field(..., description="页面ID")
    completed_at: datetime = Field(..., description="完成时间")
    status: str = Field(..., description="页面状态")


# 更新ComponentConfig的前向引用
ComponentConfig.model_rebuild()