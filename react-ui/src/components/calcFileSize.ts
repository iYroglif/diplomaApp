export default function calcFileSize(size: number) {
    if (size < 1024) {
        return size + ' bytes';
    }

    if (size < 1048576) {
        return (size / 1024).toFixed(2) + ' KB';
    }

    return (size / 1048576).toFixed(2) + ' MB';
}