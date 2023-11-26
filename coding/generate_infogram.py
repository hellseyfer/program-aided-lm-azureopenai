# filename: generate_infogram.py
html_content = """
<!DOCTYPE html>
<html>
<head>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        body {
            background-color: #f3f3f3; 
            font-family: Arial, sans-serif; 
            color: #333;
            background-image: url('background.png');
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
        }
        
        .info-card {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            width: 80%; 
            margin: 20px auto; 
            background-color: rgba(255,255,255,.8); 
            border-radius: 5px; 
            padding: 20px; 
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        .info-card i {
            font-size: 30px; 
            color: #800080; 
            margin-right: 10px; 
            vertical-align: middle;
        }
        
        .info-card .title {
            grid-column: span 2;
            font-size: 20px; 
            color: #800080; 
            font-weight: bold; 
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="info-card">
        <h1 class="title">Economic Snapshot (Month/Year)</h1>
        <div><i class="material-icons" style="color: violet;">inflation</i> Monthly Inflation: 14%</div>
        <div><i class="material-icons" style="color: violet;">crime</i> Crime Cases: 2000</div>
        <div><i class="material-icons" style="color: violet;">change</i> PBI Change: +1.2%</div>
        <div><i class="material-icons" style="color: violet;">mood</i> Overall Mood: Good</div>
    </div>
</body>
</html>
"""

with open('index.html', 'w') as f:
    f.write(html_content)
