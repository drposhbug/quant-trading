' Runs one of the pipeline jobs with NO console window (Task Scheduler
' otherwise flashes a cmd box on every run). Usage: wscript run_hidden.vbs <job>
' where <job> is daily | trader | news. Output still appends to the same logs.
Set sh = CreateObject("WScript.Shell")
here = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
sh.CurrentDirectory = here
py = "C:\Users\tyler\AppData\Local\Programs\Python\Python313\python.exe"

job = "daily"
If WScript.Arguments.Count > 0 Then job = LCase(WScript.Arguments(0))

Select Case job
  Case "trader"
    cmd = """" & py & """ trader.py --once --quiet >> trader_dry.log 2>&1"
  Case "news"
    cmd = """" & py & """ news_watch.py >> news_watch.log 2>&1"
  Case Else
    cmd = """" & here & "\run_daily.bat"""
End Select

sh.Run "cmd /c " & cmd, 0, False
