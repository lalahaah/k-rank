import { Navbar } from "@/components/navbar";
import { Footer } from "@/components/footer";

export default function PrivacyPage() {
    return (
        <div className="min-h-screen bg-white">
            <Navbar />

            <main className="max-w-4xl mx-auto px-4 py-16">
                {/* English Version */}
                <article className="prose prose-slate max-w-none mb-20">
                    <h1 className="text-4xl font-black tracking-tight text-slate-900 mb-8">Privacy Policy</h1>
                    <p className="text-sm text-slate-500 mb-8 italic">Last Updated: January 18, 2026</p>

                    <div className="space-y-8 text-slate-600 leading-relaxed">
                        <section>
                            <p>
                                <strong>Next Idea Lab Co., Ltd.</strong> ("we," "our," or "us") operates the website
                                <a href="https://k-rank.vercel.app" className="text-brand-500 hover:underline mx-1">https://k-rank.vercel.app</a>
                                (the "Service"). This page informs you of our policies regarding the collection, use, and disclosure of personal data when you use our Service and the choices you have associated with that data.
                            </p>
                            <p className="mt-4">
                                By using the Service, you agree to the collection and use of information in accordance with this policy.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">1. Information We Collect</h2>
                            <h3 className="text-lg font-bold text-slate-800 mb-2">1.1. Personal Data</h3>
                            <p>
                                While using our Service, we may ask you to provide us with certain personally identifiable information that can be used to contact or identify you ("Personal Data"). This includes:
                            </p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>Email Address:</strong> Collected when you subscribe to our newsletter, waitlist, or alerts.</li>
                                <li><strong>Usage Data:</strong> Cookies and Usage Data.</li>
                            </ul>

                            <h3 className="text-lg font-bold text-slate-800 mt-6 mb-2">1.2. Usage Data</h3>
                            <p>
                                We may also collect information on how the Service is accessed and used ("Usage Data"). This Usage Data may include information such as your computer's Internet Protocol address (e.g. IP address), browser type, browser version, the pages of our Service that you visit, the time and date of your visit, the time spent on those pages, and other diagnostic data.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">2. How We Use Your Data</h2>
                            <p><strong>Next Idea Lab Co., Ltd.</strong> uses the collected data for various purposes:</p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li>To provide and maintain the Service.</li>
                                <li>To notify you about changes to our Service.</li>
                                <li>To allow you to participate in interactive features (e.g., Waitlist) when you choose to do so.</li>
                                <li>To provide customer care and support.</li>
                                <li>To monitor the usage of the Service.</li>
                                <li>To detect, prevent and address technical issues.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">3. Data Sources & Disclaimer (Important)</h2>
                            <h3 className="text-lg font-bold text-slate-800 mb-2">3.1. Publicly Available Information</h3>
                            <p>
                                K-RANK acts as an AI-powered information curator for Korean trends. We use automated technologies to analyze publicly available data from various sources (e.g., Olive Young, Hwahae, Glowpick) to provide AI-curated rankings and trend insights.
                            </p>
                            <h3 className="text-lg font-bold text-slate-800 mt-6 mb-2">3.2. Intellectual Property & Fair Use</h3>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>Product Data:</strong> Product names, brands, and rankings displayed on the Service are factual information and are not subject to copyright.</li>
                                <li><strong>Images:</strong> Product thumbnails displayed are for <strong>identification purposes only</strong> under the principles of "Fair Use" or are provided directly via authorized Affiliate APIs (e.g., Amazon Associates).</li>
                                <li><strong>Ownership:</strong> We do not claim ownership of the underlying products or trademarks listed. All trademarks, logos, and brand names are the property of their respective owners.</li>
                                <li><strong>No Affiliation:</strong> Unless explicitly stated, <strong>Next Idea Lab Co., Ltd.</strong> is not directly affiliated with the data sources (e.g., Olive Young, Hwahae, Glowpick).</li>
                            </ul>
                            <p className="mt-4">
                                If you are a copyright owner and believe that your content has been displayed in a way that constitutes copyright infringement, please contact us at the email below for immediate removal.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">4. Affiliate Disclosure</h2>
                            <p>
                                K-RANK is a participant in the <strong>Amazon Services LLC Associates Program</strong>, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com.
                            </p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li>When you click on links to various merchants on this site and make a purchase, this can result in this site earning a commission. Affiliate programs and affiliations include, but are not limited to, the eBay Partner Network and Amazon Associates.</li>
                                <li>This comes at <strong>no extra cost to you</strong>.</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">5. Third-Party Service Providers</h2>
                            <p>We may employ third-party companies to facilitate our Service ("Service Providers"), including:</p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>Google Analytics / Firebase:</strong> To monitor and analyze the use of our Service.</li>
                                <li><strong>Vercel:</strong> For website hosting and infrastructure.</li>
                            </ul>
                            <p className="mt-4">
                                These third parties have access to your Personal Data only to perform these tasks on our behalf and are obligated not to disclose or use it for any other purpose.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">6. Security of Data</h2>
                            <p>
                                The security of your data is important to us, but remember that no method of transmission over the Internet, or method of electronic storage is 100% secure. While we strive to use commercially acceptable means to protect your Personal Data, we cannot guarantee its absolute security.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">7. Links to Other Sites</h2>
                            <p>
                                Our Service contains links to other sites that are not operated by us (e.g., Amazon, YesStyle). If you click on a third-party link, you will be directed to that third party's site. We strongly advise you to review the Privacy Policy of every site you visit. We have no control over and assume no responsibility for the content, privacy policies or practices of any third-party sites or services.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">8. Changes to This Privacy Policy</h2>
                            <p>
                                We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page. You are advised to review this Privacy Policy periodically for any changes.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">9. Contact Us</h2>
                            <p>If you have any questions about this Privacy Policy, please contact us:</p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>By email:</strong> nextidealab.ai@gmail.com</li>
                            </ul>
                        </section>
                    </div>
                </article>

                <hr className="border-slate-200 my-16" />

                {/* Korean Version */}
                <article className="prose prose-slate max-w-none">
                    <h1 className="text-3xl font-black tracking-tight text-slate-900 mb-8">개인정보 처리방침 (국문)</h1>
                    <p className="text-sm text-slate-500 mb-8 italic">최종 수정일: 2026년 1월 18일</p>

                    <div className="space-y-8 text-slate-600 leading-relaxed font-sans">
                        <section>
                            <p>
                                <strong>Next Idea Lab</strong>(이하 "회사")은
                                <a href="https://k-rank.vercel.app" className="text-brand-500 hover:underline mx-1">https://k-rank.vercel.app</a>
                                (이하 "서비스")를 운영하고 있습니다. 본 페이지는 사용자가 서비스를 이용할 때 발생하는 개인정보의 수집, 이용 및 공개에 대한 회사의 정책과 사용자의 권리를 안내합니다.
                            </p>
                            <p className="mt-4">
                                사용자는 본 서비스를 이용함으로써 본 정책에 따른 정보의 수집 및 이용에 동의하는 것으로 간주됩니다.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">1. 수집하는 정보</h2>
                            <h3 className="text-lg font-bold text-slate-800 mb-2">1.1. 개인정보 (Personal Data)</h3>
                            <p>
                                서비스 이용 과정에서 회사는 사용자의 신원을 확인하거나 연락을 취하기 위해 다음과 같은 식별 가능한 정보를 요구할 수 있습니다:
                            </p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>이메일 주소:</strong> 뉴스레터 구독, 웨이트리스트(Waitlist) 등록, 알림 설정 시 수집됩니다.</li>
                            </ul>

                            <h3 className="text-lg font-bold text-slate-800 mt-6 mb-2">1.2. 사용 데이터 (Usage Data)</h3>
                            <p>
                                회사는 서비스 접속 및 이용 방식에 대한 정보("사용 데이터")를 수집할 수 있습니다. 여기에는 사용자의 컴퓨터 IP 주소, 브라우저 유형 및 버전, 방문한 서비스 페이지, 방문 일시, 체류 시간 및 기타 진단 데이터가 포함됩니다.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">2. 개인정보의 이용 목적</h2>
                            <p><strong>Next Idea Lab</strong>은 수집한 데이터를 다음과 같은 목적으로 사용합니다:</p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li>서비스 제공 및 유지보수</li>
                                <li>서비스 변경 사항에 대한 안내</li>
                                <li>사용자가 참여형 기능(예: 웨이트리스트)을 이용할 수 있도록 지원</li>
                                <li>고객 지원 제공</li>
                                <li>서비스 이용 현황 모니터링 및 분석</li>
                                <li>기술적 문제 감지, 예방 및 해결</li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">3. 데이터 출처 및 면책 조항 (중요)</h2>
                            <h3 className="text-lg font-bold text-slate-800 mb-2">3.1. 공개된 정보의 수집</h3>
                            <p>
                                <strong>K-RANK</strong>는 한국의 트렌드 정보를 AI로 큐레이션하여 제공하는 서비스입니다. 회사는 자동화된 기술을 사용하여 다양한 출처(예: 올리브영, 화해, 글로우픽)에서 <strong>공개적으로 열람 가능한 데이터</strong>를 분석하여 AI 큐레이션 랭킹 및 트렌드 정보를 제공합니다.
                            </p>
                            <h3 className="text-lg font-bold text-slate-800 mt-6 mb-2">3.2. 지적재산권 및 공정이용 (Fair Use)</h3>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>제품 데이터:</strong> 서비스에 표시되는 상품명, 브랜드명, 순위 등의 정보는 사실(Fact)에 기반한 정보로서 저작권의 보호 대상이 아닙니다.</li>
                                <li><strong>이미지:</strong> 서비스에 표시되는 제품 썸네일은 사용자의 <strong>식별 편의(Identification purposes)</strong>를 위해 '공정이용(Fair Use)' 원칙에 따라 사용되거나, 제휴 파트너(예: Amazon Associates)의 공식 API를 통해 제공됩니다.</li>
                                <li><strong>소유권:</strong> 회사는 서비스에 나열된 제품이나 상표에 대한 소유권을 주장하지 않습니다. 모든 상표, 로고 및 브랜드명은 해당 소유자의 자산입니다.</li>
                                <li><strong>비제휴 명시:</strong> 별도의 명시가 없는 한, <strong>Next Idea Lab</strong>은 데이터 원천(예: 올리브영, 화해, 글로우픽)과 직접적인 제휴 관계가 없습니다.</li>
                            </ul>
                            <p className="mt-4">
                                귀하가 저작권 소유자이며 귀하의 콘텐츠가 저작권을 침해하는 방식으로 게시되었다고 판단되는 경우, 아래 연락처로 문의하시면 즉시 조치하겠습니다.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">4. 제휴 마케팅 공개 (Affiliate Disclosure)</h2>
                            <p>
                                <strong>K-RANK</strong>는 <strong>Amazon Services LLC Associates Program</strong>에 참여하고 있습니다. 이는 사이트가 Amazon.com으로 연결되는 링크를 제공하고 광고 수수료를 받을 수 있도록 설계된 제휴 마케팅 프로그램입니다.
                            </p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li>사용자가 본 사이트의 링크를 클릭하여 제휴 쇼핑몰에서 제품을 구매할 경우, 회사는 소정의 수수료를 받을 수 있습니다. 제휴 프로그램에는 eBay Partner Network, Amazon Associates 등이 포함됩니다.</li>
                                <li>이는 사용자에게 <strong>어떠한 추가 비용도 발생시키지 않습니다.</strong></li>
                            </ul>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">5. 제3자 서비스 제공자</h2>
                            <p>회사는 원활한 서비스 제공을 위해 다음과 같은 제3자 기업("서비스 제공자")을 이용할 수 있습니다:</p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>Google Analytics / Firebase:</strong> 서비스 이용 분석 및 데이터 관리</li>
                                <li><strong>Vercel:</strong> 웹사이트 호스팅 및 인프라 제공</li>
                            </ul>
                            <p className="mt-4">
                                이러한 제3자는 회사를 대신하여 업무를 수행하는 목적으로만 사용자의 개인정보에 접근할 수 있으며, 다른 목적으로 이를 공개하거나 사용할 의무가 없습니다.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">6. 데이터 보안</h2>
                            <p>
                                회사는 사용자의 데이터 보안을 중요하게 생각합니다. 그러나 인터넷을 통한 데이터 전송이나 전자적 저장 방식은 100% 안전할 수 없음을 유의해 주십시오. 회사는 개인정보 보호를 위해 상업적으로 허용되는 수단을 최선을 다해 사용하지만, 절대적인 보안을 보장할 수는 없습니다.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">7. 타 사이트 링크</h2>
                            <p>
                                본 서비스는 회사가 운영하지 않는 타 사이트(예: Amazon, YesStyle 등)로의 링크를 포함하고 있습니다. 제3자 링크를 클릭하면 해당 제3자의 사이트로 이동하게 됩니다. 회사는 제3자 사이트의 콘텐츠, 개인정보 처리방침 또는 관행에 대해 통제권이 없으며 책임을 지지 않습니다.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">8. 개인정보 처리방침의 변경</h2>
                            <p>
                                회사는 본 개인정보 처리방침을 수시로 업데이트할 수 있습니다. 변경 사항이 있을 경우 본 페이지에 새로운 개인정보 처리방침을 게시하여 사용자에게 알립니다. 사용자는 주기적으로 본 페이지를 검토하여 변경 사항을 확인하는 것이 좋습니다.
                            </p>
                        </section>

                        <section>
                            <h2 className="text-2xl font-bold text-slate-900 mb-4">9. 문의하기</h2>
                            <p>본 개인정보 처리방침에 대해 궁금한 점이 있으시면 아래로 문의해 주십시오:</p>
                            <ul className="list-disc pl-5 mt-2 space-y-1">
                                <li><strong>이메일:</strong> nextidealab.ai@gmail.com</li>
                            </ul>
                        </section>
                    </div>
                </article>
            </main>

            <Footer />
        </div>
    );
}
