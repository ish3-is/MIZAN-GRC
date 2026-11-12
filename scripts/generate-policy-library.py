"""Generate equivalent Arabic and English portfolio policy editions from one catalogue."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

POLICIES = [
    ("Information Security", "أمن المعلومات", "establish the security governance baseline", "إرساء خط أساس لحوكمة أمن المعلومات", "approved security objectives, assigned ownership, annual management review", "أهداف أمنية معتمدة وملكية محددة ومراجعة إدارية سنوية", "Program charter; management minutes; control dashboard", "ميثاق البرنامج؛ محاضر الإدارة؛ لوحة الضوابط"),
    ("Access Control", "التحكم في الوصول", "limit access to authorized business need", "قصر الوصول على الحاجة العملية المصرح بها", "manager-approved provisioning, least privilege, MFA, quarterly access review and verified revocation", "توفير الحساب بموافقة المدير وأقل صلاحية والمصادقة متعددة العوامل ومراجعة ربع سنوية والتحقق من الإلغاء", "Access ticket; MFA export; review sign-off; termination sample", "تذكرة وصول؛ تصدير المصادقة؛ اعتماد المراجعة؛ عينة إنهاء خدمة"),
    ("Information Classification and Handling", "تصنيف المعلومات والتعامل معها", "apply handling safeguards according to information sensitivity", "تطبيق ضوابط التعامل وفق حساسية المعلومات", "Public, Internal, Confidential and Restricted labels with storage, sharing and disposal rules", "تصنيفات عام وداخلي وسري ومقيد مع قواعد التخزين والمشاركة والإتلاف", "Data inventory; label sample; sharing approval; disposal record", "جرد البيانات؛ عينة تصنيف؛ موافقة مشاركة؛ سجل إتلاف"),
    ("Identity and Authentication", "الهوية والمصادقة", "manage identities and authentication factors throughout their lifecycle", "إدارة الهويات وعوامل المصادقة طوال دورة حياتها", "unique identities, strong authentication, protected recovery and privileged authentication review", "هويات فريدة ومصادقة قوية واسترداد محمي ومراجعة مصادقة الحسابات المميزة", "Identity export; MFA coverage; recovery test; privileged sample", "تصدير الهوية؛ تغطية المصادقة؛ اختبار الاسترداد؛ عينة الحسابات المميزة"),
    ("Acceptable Use", "الاستخدام المقبول", "define acceptable use of company technology and information", "تحديد الاستخدام المقبول لتقنية ومعلومات الشركة", "business use, prohibited behavior, device care, reporting and monitoring notice", "الاستخدام العملي والسلوك المحظور والعناية بالأجهزة والإبلاغ وإشعار المراقبة", "Acknowledgement; awareness record; exception; investigation ticket", "إقرار؛ سجل توعية؛ استثناء؛ تذكرة تحقيق"),
    ("Asset Management", "إدارة الأصول", "maintain accountable and current information-asset ownership", "الحفاظ على ملكية مسؤولة ومحدثة للأصول المعلوماتية", "inventory, owner, classification, lifecycle status and secure return or disposal", "جرد ومالك وتصنيف وحالة دورة حياة وإرجاع أو إتلاف آمن", "Asset register; owner attestation; disposal certificate", "سجل الأصول؛ إقرار المالك؛ شهادة الإتلاف"),
    ("Vulnerability and Patch Management", "إدارة الثغرات والتحديثات", "identify and treat technical weaknesses according to risk", "تحديد ومعالجة نقاط الضعف التقنية وفق المخاطر", "authenticated scanning, risk triage, approved remediation targets, exceptions and retest", "فحص موثق وفرز مخاطر وأهداف معالجة معتمدة واستثناءات وإعادة اختبار", "Scan report; remediation ticket; exception approval; retest", "تقرير فحص؛ تذكرة معالجة؛ اعتماد استثناء؛ إعادة اختبار"),
    ("Incident Response", "الاستجابة للحوادث", "coordinate reporting, containment, investigation and recovery", "تنسيق الإبلاغ والاحتواء والتحقيق والتعافي", "reporting, severity, ownership, escalation, evidence preservation, notification assessment and lessons learned", "الإبلاغ والشدة والملكية والتصعيد وحفظ الأدلة وتقييم الإشعار والدروس المستفادة", "Incident timeline; evidence log; approvals; lessons learned", "الخط الزمني للحادث؛ سجل الأدلة؛ الاعتمادات؛ الدروس المستفادة"),
    ("Business Continuity and Backup", "استمرارية الأعمال والنسخ الاحتياطي", "recover critical services within approved objectives", "استعادة الخدمات الحرجة ضمن الأهداف المعتمدة", "BIA, RTO, RPO, monitored backup, protected retention, restore testing and escalation", "تحليل الأثر وRTO وRPO ومراقبة النسخ والاحتفاظ المحمي واختبار الاستعادة والتصعيد", "BIA; backup log; restore result; continuity exercise", "تحليل الأثر؛ سجل النسخ؛ نتيجة الاستعادة؛ تمرين الاستمرارية"),
    ("Change Management", "إدارة التغيير", "introduce technology change with controlled risk", "تنفيذ التغيير التقني ضمن مخاطر مضبوطة", "request, justification, risk assessment, test, approval, deployment, rollback and post-review", "طلب ومبرر وتقييم مخاطر واختبار واعتماد ونشر وتراجع ومراجعة لاحقة", "Change ticket; test result; approval; deployment and rollback log", "تذكرة تغيير؛ نتيجة اختبار؛ اعتماد؛ سجل نشر وتراجع"),
    ("Third-Party and Vendor Security", "أمن الأطراف الثالثة والموردين", "manage supplier security and privacy risk throughout the relationship", "إدارة مخاطر أمن وخصوصية المورد طوال العلاقة", "classification, due diligence, questionnaire, contract requirements, DPA tracking, review and offboarding", "تصنيف وعناية واجبة واستبيان ومتطلبات تعاقدية وتتبع اتفاقية المعالجة ومراجعة وإنهاء", "Questionnaire; due diligence; contract review; offboarding record", "استبيان؛ عناية واجبة؛ مراجعة عقد؛ سجل إنهاء"),
    ("Risk Management", "إدارة المخاطر", "apply a consistent and explainable risk process", "تطبيق عملية مخاطر متسقة وقابلة للتفسير", "context, 5×5 rating, inherent and residual rationale, treatment, ownership, review and acceptance approval", "سياق وتقييم 5×5 ومبرر كامن ومتبق ومعالجة وملكية ومراجعة واعتماد القبول", "Risk record; assessment rationale; treatment plan; acceptance decision", "سجل مخاطر؛ مبرر التقييم؛ خطة معالجة؛ قرار قبول"),
    ("Data Protection and Privacy", "حماية البيانات والخصوصية", "govern personal-data processing and demonstrable accountability", "حوكمة معالجة البيانات الشخصية وإثبات المساءلة", "inventory, purpose, legal-basis validation, notices, rights routing, processor oversight and impact assessment", "جرد وغرض والتحقق من المسوغ والإشعارات وتوجيه الحقوق وإشراف المعالج وتقييم الأثر", "RoPA; legal review; privacy notice; processor assessment; PIA", "سجل المعالجة؛ مراجعة قانونية؛ إشعار خصوصية؛ تقييم معالج؛ تقييم أثر"),
    ("Data Retention and Disposal", "الاحتفاظ بالبيانات والتخلص منها", "retain information only for an approved purpose and period", "الاحتفاظ بالمعلومات لغرض ومدة معتمدين فقط", "approved schedule, legal hold, deletion authorization, secure disposal and verification", "جدول معتمد وتعليق نظامي وتفويض حذف وإتلاف آمن وتحقق", "Retention schedule; legal hold; deletion ticket; disposal verification", "جدول الاحتفاظ؛ تعليق نظامي؛ تذكرة حذف؛ تحقق الإتلاف"),
    ("Remote Access", "الوصول عن بعد", "protect remote connections to company services", "حماية الاتصالات عن بعد بخدمات الشركة", "approved users, managed devices, MFA, encrypted connection, monitoring and periodic review", "مستخدمون معتمدون وأجهزة مُدارة ومصادقة متعددة واتصال مشفر ومراقبة ومراجعة دورية", "Remote-access group; device compliance; MFA export; access review", "مجموعة الوصول؛ امتثال الجهاز؛ تصدير المصادقة؛ مراجعة الوصول"),
    ("Logging and Monitoring", "التسجيل والمراقبة", "produce and review security-relevant records", "إنتاج ومراجعة السجلات ذات الصلة بالأمن", "defined sources, synchronized time, protected logs, alert rules, triage, escalation and retention", "مصادر محددة ووقت متزامن وسجلات محمية وقواعد تنبيه وفرز وتصعيد واحتفاظ", "Source inventory; time check; alert sample; triage ticket; retention setting", "جرد المصادر؛ تحقق الوقت؛ عينة تنبيه؛ تذكرة فرز؛ إعداد الاحتفاظ"),
]


def render(index, item, language):
    en_title, ar_title, en_purpose, ar_purpose, en_req, ar_req, en_ev, ar_ev = item
    pid = f"NAM-POL-{index:03}"
    if language == "en":
        title, purpose, requirement, evidence = en_title, en_purpose, en_req, en_ev
        return f"""# {pid} — {title} Policy

> SIMULATED DATA — NOT REAL ORGANIZATIONAL EVIDENCE. Portfolio policy for Namaa Digital Solutions. It is not legal advice, certification or regulator approval.

| Field | Value |
|---|---|
| Owner | GRC Manager / assigned control owner |
| Reviewer | GRC Analyst |
| Approver | Internal Auditor or authorized executive, separated from the owner |
| Classification | Internal |
| Version | 1.0 simulation |
| Review cycle | Annual organizational cycle; not a regulatory deadline |

## Purpose and scope

This policy exists to {purpose}. It applies to fictional employees, contractors, information assets, business services and in-scope suppliers of Namaa Digital Solutions.

## Mandatory requirements

1. The organization shall maintain {requirement}.
2. The accountable owner shall define the population, frequency and system of record.
3. Operation shall be supported by dated, attributable evidence; a document alone does not prove implementation.
4. An exception requires justification, affected scope, risk assessment, compensating controls, approval and an expiry date.

## Operational procedure

1. Identify the in-scope population and accountable owner.
2. Open or update the approved ticket, register or workflow before the activity.
3. Perform the control and preserve the expected evidence without real personal data in the demonstration.
4. Review failures and exceptions, assign remediation and escalate overdue actions.
5. An independent reviewer samples the operation and records a pass, partial result or failure.

## Implementation checklist

- Owner and scope approved.
- Procedure published and communicated.
- Tool or register configured.
- Representative operating sample collected.
- Exceptions and overdue actions reviewed.
- Independent effectiveness test recorded.

## Evidence and testing

Expected evidence: {evidence}.

The assessor inspects the approval, samples operating records from the stated period, traces exceptions to decisions, and reperforms one check. The report distinguishes document existence, approval, publication, acknowledgement, procedure implementation, control operation, evidence verification and independent testing.

## Mapping and exceptions

Mappings use Namaa organizational control IDs unless a separately verified source record is cited. No ISO clause wording is reproduced. Exceptions follow the MIZAN exception workflow and automatically return for review at expiry.
"""
    title, purpose, requirement, evidence = ar_title, ar_purpose, ar_req, ar_ev
    return f"""# {pid} — سياسة {title}

> بيانات محاكاة — ليست أدلة تنظيمية حقيقية. سياسة مهنية تجريبية لشركة نماء للحلول الرقمية، ولا تمثل مشورة قانونية أو شهادة اعتماد أو موافقة جهة تنظيمية.

| الحقل | القيمة |
|---|---|
| المالك | مدير الحوكمة والمخاطر والامتثال / مالك الضابط المعين |
| المراجع | محلل الحوكمة والمخاطر والامتثال |
| المعتمد | المدقق الداخلي أو مسؤول تنفيذي مخول مستقل عن المالك |
| التصنيف | داخلي |
| الإصدار | 1.0 تجريبي |
| دورة المراجعة | دورة تنظيمية سنوية؛ وليست مهلة نظامية |

## الغرض والنطاق

تهدف هذه السياسة إلى {purpose}. وتسري على الموظفين والمتعاقدين والأصول المعلوماتية والخدمات العملية والموردين المشمولين في البيئة الافتراضية لشركة نماء للحلول الرقمية.

## المتطلبات الإلزامية

1. تحافظ المنشأة على {requirement}.
2. يحدد المالك المسؤول المجتمع المشمول والتكرار ونظام السجل.
3. يدعم التشغيل دليل مؤرخ ومنسوب إلى مصدره؛ ولا يثبت وجود الوثيقة وحده التطبيق.
4. يتطلب الاستثناء مبرراً ونطاقاً متأثراً وتقييم مخاطر وضوابط تعويضية واعتماداً وتاريخ انتهاء.

## الإجراء التشغيلي

1. تحديد المجتمع المشمول والمالك المسؤول.
2. فتح أو تحديث التذكرة أو السجل أو سير العمل المعتمد قبل تنفيذ النشاط.
3. تشغيل الضابط وحفظ الدليل المتوقع دون بيانات شخصية حقيقية في بيئة العرض.
4. مراجعة الإخفاقات والاستثناءات وإسناد المعالجة وتصعيد الإجراءات المتأخرة.
5. يأخذ مراجع مستقل عينة من التشغيل ويسجل نتيجة ناجحة أو جزئية أو إخفاقاً.

## قائمة التحقق من التطبيق

- اعتماد المالك والنطاق.
- نشر الإجراء وإيصاله.
- تهيئة الأداة أو السجل.
- جمع عينة تشغيل ممثلة.
- مراجعة الاستثناءات والإجراءات المتأخرة.
- تسجيل اختبار فعالية مستقل.

## الأدلة والاختبار

الأدلة المتوقعة: {evidence}.

يفحص المقيم الاعتماد، ويأخذ عينة من سجلات التشغيل للفترة المحددة، ويربط الاستثناءات بالقرارات، ويعيد تنفيذ فحص واحد. ويفصل التقرير بين وجود الوثيقة واعتمادها ونشرها والإقرار بها وتطبيق الإجراء وتشغيل الضابط والتحقق من الدليل والاختبار المستقل.

## الربط والاستثناءات

تستخدم الروابط معرفات ضوابط نماء التنظيمية ما لم يُستشهد بسجل مصدر متحقق منه بصورة مستقلة. لا يُعاد نشر نصوص بنود ISO. وتتبع الاستثناءات سير الاستثناء في ميزان وتعود للمراجعة عند انتهاء مدتها.
"""


def main():
    for language in ("en", "ar"):
        folder = ROOT / "docs" / language / "policies"
        folder.mkdir(parents=True, exist_ok=True)
        links = []
        for index, item in enumerate(POLICIES, start=1):
            slug = item[0].lower().replace(" ", "-").replace("/", "-")
            path = folder / f"NAM-POL-{index:03}-{slug}.md"
            path.write_text(render(index, item, language), encoding="utf-8")
            links.append(f"- [{path.stem}]({path.name})")
        heading = "# Namaa policy library" if language == "en" else "# مكتبة سياسات نماء"
        (folder / "README.md").write_text(heading + "\n\n" + "\n".join(links) + "\n", encoding="utf-8")
    print("Generated 32 equivalent policy editions and two indexes.")


if __name__ == "__main__":
    main()
