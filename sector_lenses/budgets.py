"""Platform-wide limits shared by lens loading and prompt-slice assembly."""

from .models import StageBudgets


MAX_ACTIVE_LENSES = 2
# Stage 2 raised 2000 -> 3000 for the climate readout redesign: the climate-native
# Stage 2 suffix now injects the triggered core-question bank + the OPCS Section 12
# recommendation-calibration guardrails on top of the existing dedicated-module contract.
PLATFORM_STAGE_BUDGETS = StageBudgets(stage1=600, stage2=3000, stage3=1600)
