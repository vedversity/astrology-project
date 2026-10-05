import { RashifalPage, rashifalMetadata } from "@/components/daily";

type Props = { params: Promise<{ rashi: string }> };

export async function generateMetadata({ params }: Props) {
  return rashifalMetadata("hi", (await params).rashi);
}

export default async function Page({ params }: Props) {
  return <RashifalPage lang="hi" slug={(await params).rashi} />;
}
