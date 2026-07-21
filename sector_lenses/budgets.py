"""Platform-wide limits shared by lens loading and prompt-slice assembly."""

from .models import StageBudgets


MAX_ACTIVE_LENSES = 2
PLATFORM_STAGE_BUDGETS = StageBudgets(stage1=600, stage2=2000, stage3=900)
