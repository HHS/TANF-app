import { open } from 'k6/experimental/fs';

export let Section1File;
export let Section2File;
export let Section3File;
export let Section4File;

(async function() {
  Section1File = await open('../data/ADS.E2J.FTP1.TS06')
  Section2File = await open('../data/ADS.E2J.FTP2.TS06')
  Section3File = await open('../data/ADS.E2J.FTP3.TS06')
  Section4File = await open('../data/ADS.E2J.FTP4.TS06')
})()

// readAll will read the whole of the file from the local filesystem into a
// buffer.
export const readAll = async (file) => {
  const fileInfo = await file.stat();
  const buffer = new Uint8Array(fileInfo.size);

  const bytesRead = await file.read(buffer);
  if (bytesRead !== fileInfo.size) {
    throw new Error('unexpected number of bytes read');
  }

  return buffer;
}