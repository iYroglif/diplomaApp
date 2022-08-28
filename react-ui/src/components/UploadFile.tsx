import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import "./UploadFile.css"

export const UploadFile = () => {
  const [file, setFile] = useState<File | null>(null);
  const [dragEntered, setDragEntered] = useState(false)
  const navigate = useNavigate()

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      handleSetFile(event.target.files[0])
    }
  }

  useEffect(() => {
    if (file) {
      const formData = new FormData();
      formData.set('file', file, file.name);
      fetch('/api/upload', {
        method: 'POST',
        body: formData,
      }).then((res) => {
        if (res.ok)
          return res.json()
        else {
          setDragEntered(false)
          throw new Error('Произошла ошибка при загрузке файла. Проверьте, что расширение файла поддерживается, и попробуйте снова.')
        }
      }).then((data) => navigate('/preview/' + data.file_id))
        .catch((e) => alert(e));
    }
  }, [file, navigate])

  const handleSetFile = (file: File) => {
    if (file.type.includes('mp4') || file.type.includes('avi'))
      setFile(file)
    else
      return
  }

  const handleDragEnter = () => {
    setDragEntered(true)
  }

  const handleDragLeave = () => {
    setDragEntered(false)
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragEntered(true)
    //event.stopPropagation()
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    handleSetFile(event.dataTransfer.files[0])
    setDragEntered(false)
  }

  let dragAreaDisplay = 'none'

  if (dragEntered)
    dragAreaDisplay = ''
  else
    dragAreaDisplay = 'none'

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