import { EncodingType, File, Paths } from "expo-file-system";

export async function fileUriToBase64(uri: string): Promise<string> {
  const file = new File(uri);
  return file.base64();
}

export function writeBase64ToCacheFile(base64: string, extension: string): string {
  const file = new File(Paths.cache, `voice-reply-${Date.now()}${extension}`);
  file.write(base64, { encoding: EncodingType.Base64 });
  return file.uri;
}
