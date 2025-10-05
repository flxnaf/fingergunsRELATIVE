# Relative Mouse Positioning for FPS Games

## Overview
The fingergun backend has been updated to use **relative mouse positioning** instead of absolute positioning, making it perfect for FPS games where you need continuous mouse movement.

## What Changed

### Before (Absolute Positioning)
- Hand position directly mapped to screen coordinates
- Used `pyautogui.moveTo(x, y)` to set absolute cursor position
- Cursor would jump to match hand position
- Limited by screen boundaries

### After (Relative Positioning)
- Hand movement translates to cursor movement (like a mouse)
- Used `pyautogui.moveRel(dx, dy)` for relative movement
- Cursor moves based on how much your hand moves
- **System remembers last hand position** and only moves based on the delta

## How It Works

1. **Position Tracking**: The system tracks your index finger's position in each frame
2. **Delta Calculation**: It calculates the difference (delta) between current and last position
3. **Relative Movement**: The cursor moves by the calculated delta amount
4. **Sensitivity Control**: Movement can be scaled with a sensitivity multiplier
5. **Smart Reactivation**: When gun gesture is released and re-activated, position is reestablished WITHOUT snapping (no absolute positioning)

## Key Features

✅ **Remembers Last Position**: Tracks hand position frame-by-frame  
✅ **NO SNAPPING**: When gun gesture is released and re-locked, cursor stays put (true relative positioning)  
✅ **Smooth Movement**: No jumping or jittering  
✅ **FPS Game Ready**: Works perfectly with games that use relative mouse input  
✅ **Configurable Sensitivity**: Adjust `sensitivity` parameter (default: 1.0)  
✅ **Smart Reactivation**: First frame after re-lock establishes baseline without moving cursor  

## Updated Files

- `integrated_control_system.py` - Main control system
- `dual_hand_tracking.py` - Dual hand tracking system
- `finger_tracking.py` - Basic finger tracking
- `leaning_control_system.py` - Already had relative positioning implemented!

## Usage

The relative positioning is automatic when using any of the control systems:

```python
# The mouse controller now works with relative positioning
mouse_controller = SmoothMouseController(sensitivity=1.0)

# In your tracking loop:
if gun_active:
    index_tip = hand_landmarks.landmark[8]
    delta_x, delta_y = mouse_controller.update(index_tip.x, index_tip.y)
    mouse_controller.move_mouse(delta_x, delta_y)
else:
    mouse_controller.reset()  # Reset tracking when gun is not active
```

## Sensitivity Adjustment

You can adjust the sensitivity when creating the controller:

```python
# Lower sensitivity (slower, more precise)
mouse_controller = SmoothMouseController(sensitivity=0.5)

# Higher sensitivity (faster movement)
mouse_controller = SmoothMouseController(sensitivity=2.0)
```

## Debug Output

The system outputs debug information every 30 frames to help you monitor movement:
```
Relative mouse delta: x=5, y=-3
```

## Testing

To test the relative positioning:

1. Run any of the control systems (e.g., `python leaning_control_system.py`)
2. Make the gun gesture (index finger out, other fingers curled)
3. Move your hand - the cursor should follow smoothly
4. Release the gesture - position tracking resets
5. Make the gesture again - cursor continues from where it is (no jumping!)

## Perfect for:
- CS:GO
- Valorant
- Call of Duty
- Any FPS game that uses relative mouse input
- Games that require continuous mouse movement

Enjoy your FPS gaming with finger guns! 🎮👈

