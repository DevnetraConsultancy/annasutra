with open('04a7810_landing.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function setFlowActiveStageUI')
print(text[pos:pos+1200])
