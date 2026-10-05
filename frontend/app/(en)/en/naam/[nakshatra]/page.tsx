import { NaamPage, naamMetadata } from "@/components/guides";

type Props = { params: Promise<{ nakshatra: string }> };

export async function generateMetadata({ params }: Props) {
  return naamMetadata("en", (await params).nakshatra);
}

export default async function Page({ params }: Props) {
  return <NaamPage lang="en" slug={(await params).nakshatra} />;
}
