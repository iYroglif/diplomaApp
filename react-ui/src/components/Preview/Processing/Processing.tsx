// @FIX sse при окончании вызывает срабатывание onerror (вызывается ли это событие при попытке переподключения -> реализовать свой ивент закрытия)

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { progressURL } from "../../../api/urls";
import { secondsToString } from "../secondsToString";
import "./Processing.css";

export const Processing = ({ fileId }: { fileId: string }) => {
  const [currentProgress, setCurrentProgress] = useState("0");
  const [timeLeft, setTimeLeft] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const eventSource = new EventSource(`${progressURL}/${fileId}`);
    let prevProgress = 0;
    let prevTime = new Date().getTime();

    eventSource.onmessage = (event) => {
      const newTime = new Date().getTime();

      setTimeLeft(Math.round((((100 - event.data) / (event.data - prevProgress)) * (newTime - prevTime)) / 1000));
      setCurrentProgress(event.data);

      prevProgress = event.data;
      prevTime = newTime;
    };

    eventSource.onerror = () => {
      eventSource.close();
      navigate(`/download/${fileId}`);
    };

    return () => {
      eventSource.close();
    };
  }, [fileId, navigate]);

  return (
    <div className="progress">
      <h2>Прогресс обработки:</h2>
      <div className="meter">
        <div className="curr-prog" style={{ width: `${currentProgress}%` }}></div>
        <span className="current-progress-text">{currentProgress}%</span>
      </div>
      <h3>Осталось времени: {timeLeft === Infinity ? "" : secondsToString(timeLeft)}</h3>
    </div>
  );
};
