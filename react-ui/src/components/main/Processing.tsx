// @FIX sse при окончании вызывает срабатывание onerror (вызывается ли это событие при попытке переподключения -> реализовать свой ивент закрытия)

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Processing.css"

let prevTime: number = (new Date()).getTime()
let prevProgress: number = 0

export const Processing = ({ fileId }: { fileId: string }) => {
  const [currentProgress, setCurrentProgress] = useState("0");
  const [timeLeft, setTimeLeft] = useState(0);
  const navigate = useNavigate()

  useEffect(() => {
    const eventSource = new EventSource("/api/progress/" + fileId);

    eventSource.onmessage = function (event) {
      let newTime = (new Date()).getTime()
      setTimeLeft(Math.round(((100 - event.data) / (event.data - prevProgress)) * (newTime - prevTime) / 1000))
      setCurrentProgress(event.data);
      prevProgress = event.data
      prevTime = newTime
    };

    eventSource.onerror = function (event) {
      eventSource.close();
      navigate('/download/' + fileId)
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="progress">
      <h2>Прогресс обработки:</h2>
      <div className="meter">
        <div className="curr-prog"
          style={{ width: `${currentProgress}%` }}>
          {currentProgress}%
        </div>
      </div>
      <h3>Осталось времени: {timeLeft} секунд</h3>
    </div>
  );
}
