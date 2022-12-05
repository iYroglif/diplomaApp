import React, { useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { uploadURL } from "../../api/urls";
import "./UploadFile.css";

export const UploadFile = () => {
  const [dragEntered, setDragEntered] = useState(false);
  const inputFile = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const uploadFile = useCallback(
    async (file: File) => {
      if (file.type.includes("mp4") || file.type.includes("avi")) {
        const formData = new FormData();

        formData.set("file", file, file.name);

        const response = await fetch(uploadURL, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          navigate(`/preview/${data.file_id}`);
        } else {
          // throw new Error('Произошла ошибка при загрузке файла. Проверьте, что расширение файла поддерживается, и попробуйте снова.');
          alert("Произошла ошибка при загрузке файла. Проверьте, что расширение файла поддерживается, и попробуйте снова.");
        }
      }
    },
    [navigate]
  );

  const handleChange = useCallback(() => {
    if (inputFile.current?.files) {
      uploadFile(inputFile.current.files[0]);
    }
  }, [uploadFile]);

  const handleDragEnter = useCallback(() => {
    setDragEntered(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragEntered(false);
  }, []);

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragEntered(true);
  }, []);

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();

      uploadFile(event.dataTransfer.files[0]);
      setDragEntered(false);
    },
    [uploadFile]
  );

  return (
    <>
      <div
        className="drop-area"
        style={{ display: dragEntered ? "" : "none" }}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      />

      <h2 className="func-name">Удалить визуальный шум из видео</h2>
      <h3 className="func-desc">Загрузите видеофайл, чтобы нейросеть удалила из него гауссовский шум</h3>

      <div className="drag-area" onDragEnter={handleDragEnter}>
        <div className="select-button">
          <label htmlFor="inputFile">Выбрать файл</label>

          <input id="inputFile" ref={inputFile} type="file" onChange={handleChange} multiple={false} accept=".mp4,.avi"></input>
        </div>

        <span className="drop-text">или просто перетащите файл</span>
      </div>

      <p>на данный момент поддерживаются форматы mp4 и avi</p>
    </>
  );
};
