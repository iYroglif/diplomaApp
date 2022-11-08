import React, { useRef, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import "./UploadFile.css"

export default function UploadFile() {
  const [dragEntered, setDragEntered] = useState(false)
  const inputFile = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const uploadFile = useCallback(async (file: File) => {
    const formData = new FormData();

    formData.set('file', file, file.name);

    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      navigate('/preview/' + data.file_id);
    } else {
      setDragEntered(false);
      // throw new Error('Произошла ошибка при загрузке файла. Проверьте, что расширение файла поддерживается, и попробуйте снова.');
      const e = new Error('Произошла ошибка при загрузке файла. Проверьте, что расширение файла поддерживается, и попробуйте снова.');
      alert(e);
    }
  }, []);

  const handleChange = useCallback(() => {
    if (inputFile.current && inputFile.current.files) {
      const file = inputFile.current.files[0];

      if (file.type.includes('mp4') || file.type.includes('avi')) {
        uploadFile(file);
      }
    }
  }, []);

  // const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  //   if (event.target.files) {
  //     handleSetFile(event.target.files[0])
  //   }
  // }

  // useEffect(() => {
  //   if (file) {
  //     const formData = new FormData();
  //     formData.set('file', file, file.name);
  //     fetch('/api/upload', {
  //       method: 'POST',
  //       body: formData,
  //     }).then((res) => {
  //       if (res.ok)
  //         return res.json()
  //       else {
  //         setDragEntered(false)
  //         throw new Error('Произошла ошибка при загрузке файла. Проверьте, что расширение файла поддерживается, и попробуйте снова.')
  //       }
  //     }).then((data) => navigate('/preview/' + data.file_id))
  //       .catch((e) => alert(e));
  //   }
  // }, [file, navigate])

  // const handleSetFile = (file: File) => {
  //   if (file.type.includes('mp4') || file.type.includes('avi'))
  //     setFile(file)
  //   else
  //     return
  // }

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

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    uploadFile(event.dataTransfer.files[0]);
    setDragEntered(false);
  }, []);

  const dragAreaDisplay = dragEntered ? "" : "none";

  return (
    <>
      <div className='drag-area'
        style={{ display: dragAreaDisplay }}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}>
        Отпустите файл
      </div>

      <div className='upload-file'>

        <h2 className='func-name'>Удалить визуальный шум из видео</h2>
        <h3 className='func-desc'>Загрузите видеофайл, чтобы нейросеть удалила из него гауссовский шум</h3>

        <div className='drop-area'
          onDragEnter={handleDragEnter}>

          <div className='select-button'>
            <label htmlFor='inputFile'
              style={{ cursor: 'pointer', padding: '25px 80px' }}>
              Выбрать файл
            </label>

            <input id='inputFile'
              ref={inputFile}
              type='file'
              onChange={handleChange}
              multiple={false}
              // accept='video/*,image/*'
              accept='video/*'
              style={{ display: 'none' }}>
            </input>
          </div>

          <span className='drop-text'>или просто перетащите файл</span>
        </div>

        <p>на данный момент поддерживаются форматы mp4 и avi</p>
      </div>
    </>
  );
}