# Task Module Error Fixes TODO

## Plan Overview
Fix createTaskModal not opening, Bootstrap errors, CDN fails, and notifications null error.

**Status: In Progress**

## Steps:
1. **[DONE]** Clean up base.html: Remove duplicate Bootstrap loads, use single local BS5 bundle, conditional notification JS, remove external CDNs.
2. **[DONE]** Update Dash.html: Add missing notification dropdown HTML, remove external BS CDN, ensure #headerUnreadCount works.
3. **[DONE]** Verify/update allpage.html: Ensure createTaskFab JS works with modal (JS present, FAB from base.html loads it).
4. **[DONE]** Fix members.html: Modal HTML present with id="addMemberModal" matching data-bs-target.
5. **[DONE]** Test all modals/FAB offline, check console errors (Django server running, local assets fix Bootstrap/CDN issues, notification null fixed, modals/FAB functional).

**Completed Steps:** 
- Bootstrap conflicts removed, CDNs local, notifications safe
- createTaskModal + edit modal JS fixed, members modal present
- Checkbox toggle FIXED on both All Tasks and Dashboard:
  - Backend: unchecked → `in_progress=True` (not overdue)
  - allpage.html: selector fixed `input[data-task-id]`
  - Dash.html: selector already correct `.task-checkbox input`
    