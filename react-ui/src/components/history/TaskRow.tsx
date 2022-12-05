import { TaskRowProps } from "./TaskRowPropsInterface";
import { calcFileSize } from "../calcFileSize";
import { downloadURL } from "../../api/urls";

export const TaskRow = ({ id, file_name, file_size, date }: TaskRowProps) => {
  return (
    <tr>
      <td>{file_name}</td>
      <td>{calcFileSize(file_size)}</td>
      <td>{new Date(date).toLocaleString()}</td>
      <td>
        <a href={`${downloadURL}/${id}`}>
          <button className="btn btn-primary">Скачать</button>
        </a>
      </td>
    </tr>
  );
};
