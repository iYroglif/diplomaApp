import { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import { calcFileSize } from "../calcFileSize";
import { useFetchBlob } from "./useFetchBlob";
import "./Preview.css";
import { Processing } from "./Processing/Processing";
import { useFetchJSON } from "../../useFetchJSON";
import { filePropsURL, imgDenoisedURL, imgPreviewURL } from "../../api/urls";
import { secondsToString } from "./secondsToString";

interface FileProps {
  name: string;
  size: number;
  width: number;
  height: number;
  numframes: number;
}

export const Preview = () => {
  const params = useParams();
  const [fileProps, filePropsError] = useFetchJSON<FileProps>(`${filePropsURL}/${params.fileId}`);
  const [imgOrig, imgOrigError] = useFetchBlob(`${imgPreviewURL}/${params.fileId}`);
  const [imgDen, imgDenError] = useFetchBlob(`${imgDenoisedURL}/${params.fileId}`);
  const [isSubmitted, setIsSubmitted] = useState(false);

  let imgOrigUrl;
  if (imgOrigError) {
    console.error(imgOrigError);
    // @TODO обработка того что файл не найден на сервере
  } else if (imgOrig) {
    imgOrigUrl = URL.createObjectURL(imgOrig);
  }

  let imgDenUrl;
  if (imgDenError) {
    console.error(imgDenError);
    // @TODO обработка того что файл не найден на сервере
  } else if (imgDen) {
    imgDenUrl = URL.createObjectURL(imgDen);
  }

  const handleClick = useCallback(() => {
    setIsSubmitted(true);
  }, []);

  if (params.fileId && fileProps && !filePropsError) {
    return (
      <>
        {isSubmitted ? (
          <Processing fileId={params.fileId} />
        ) : (
          <>
            <div className="preview-imgs">
              <div className="file-preview">
                <p>Имя файла: {fileProps.name}</p>
                {imgOrigUrl && <img src={imgOrigUrl} alt="Исходный кадр" />}
                <p>Размер файла: {calcFileSize(fileProps.size)}</p>
              </div>
              <div className="file-preview-denoised">
                <p>Превью обработки файла:</p>
                {imgDenUrl && <img src={imgDenUrl} alt="Обработанный кадр" />}
                <div className="preview-subm">
                  <p>
                    {`Примерное время обработки: ${secondsToString(
                      Math.round((fileProps.height * fileProps.width * fileProps.numframes) / 103000)
                    )}`}
                  </p>
                  <div className="btn-start" onClick={handleClick}>
                    Удалить шум
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </>
    );
  } else {
    return <p>Файл не существует</p>;
  }
};
