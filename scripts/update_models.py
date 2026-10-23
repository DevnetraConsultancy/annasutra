path = 'backend/apps/identity/models.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target1 = '''    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("NEEDS_CHANGES", "Needs Changes"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
        ("SUSPENDED", "Suspended"),
    ]'''

repl1 = '''    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SUBMITTED", "Submitted"),
        ("NEEDS_CHANGES", "Needs Changes"),
        ("VERIFIED", "Verified"),
        ("REJECTED", "Rejected"),
        ("SUSPENDED", "Suspended"),
        ("TRASH", "Trash"),
    ]'''

target2 = '''    DECISION_CHOICES = [
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("NEEDS_CHANGES", "Needs Changes"),
        ("SUSPENDED", "Suspended"),
    ]'''

repl2 = '''    DECISION_CHOICES = [
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("NEEDS_CHANGES", "Needs Changes"),
        ("SUSPENDED", "Suspended"),
        ("TRASH", "Moved to Trash"),
        ("RESTORED", "Restored"),
    ]'''

text = text.replace(target1, repl1).replace(target2, repl2)
with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("Done")
