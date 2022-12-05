import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { downloadURL } from "../../api/urls";
import "./Download.css";

export const Download = () => {
  const params = useParams();

  useEffect(() => {
    document.location.href = `${downloadURL}/${params.fileId}`;
  }, [params.fileId]);

  return (
    <>
      {params.fileId ? (
        <>
          <h3>Скачивание файла начнется автоматически, если нет нажмите на кнопку:</h3>
          <a className="download-btn" href={`${downloadURL}/${params.fileId}`}>
            Скачать файл
          </a>
        </>
      ) : (
        <p>Файл не существует</p>
      )}
    </>
  );
};
