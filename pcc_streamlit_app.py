import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

class CodingTestMonitor:
    def __init__(self):
        self.columns = ['No.', '시험과목', '이메일', '합격여부', '총점', '등급(Lv.)', '학과', '학년', '학번']
        self.data = pd.DataFrame(columns=self.columns)
        self.test_rounds = []
        self.all_rounds_data = {}  # 모든 회차 데이터 저장

    def load_data(self, file):
        """파일에서 데이터를 로드하고 데이터 타입을 변환합니다."""
        try:
            # 파일 로드
            df = self._load_file(file)
            if df is None:
                return False
            
            # 데이터 타입 변환 및 결측값 처리
            self._process_data_types(df)
            self.data = df
            return True
            
        except Exception as e:
            st.error(f"파일 로드 중 오류 발생: {e}")
            return False

    def _load_file(self, file):
        """파일 형식에 따라 데이터를 로드합니다."""
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file)
        return None

    def _process_data_types(self, df):
        """데이터 타입 변환 및 결측값 처리를 수행합니다."""
        # No. 컬럼을 정수형으로 변환
        if 'No.' in df.columns:
            df['No.'] = pd.to_numeric(df['No.'], errors='coerce').astype('Int64')

        # 총점을 float64로 변환
        if '총점' in df.columns:
            df['총점'] = pd.to_numeric(df['총점'], errors='coerce').astype('float64')

        # 학년을 문자열로 변환
        if '학년' in df.columns:
            df['학년'] = df['학년'].astype(str)

        # 문자열 컬럼들의 타입 변환
        string_columns = ['시험과목', '이메일', '합격여부', '등급(Lv.)', '학과', '학번']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)

        # 결측값 처리
        df.fillna({'총점': 0, '학년': '1', 'No.': 1}, inplace=True)

    def filter_data(self, filters):
        """주어진 조건으로 데이터를 필터링합니다."""
        try:
            filtered_data = self.data.copy()
            for key, value in filters.items():
                if value:  # 값이 존재하는 경우에만 필터링
                    filtered_data = self._apply_filter(filtered_data, key, value)
            return filtered_data
        
        except Exception as e:
            st.error(f"필터링 중 오류 발생: {e}")
            return self.data

    def _apply_filter(self, data, key, value):
        """특정 키에 대한 필터를 적용합니다."""
        if isinstance(value, list):
            return data[data[key].isin(value)]
        elif key == '학년':
            return data[data[key].astype(str) == str(value)]
        else:
            return data[data[key] == value]

    def get_statistics(self, data):
        """기본 통계 정보를 계산합니다."""
        try:
            stats = {
                '총 응시자 수': len(data),
                '합격률': (data['합격여부'] == '합격').mean() * 100,
                '평균 점수': data['총점'].mean(),
                '학과별 응시자 수': data['학과'].value_counts().to_dict(),
                '학년별 응시자 수': data['학년'].value_counts().to_dict(),
                '등급별 분포': data['등급(Lv.)'].value_counts().to_dict()
            }
            return stats
        except Exception as e:
            st.error(f"통계 계산 중 오류 발생: {e}")
            return {
                '총 응시자 수': 0,
                '합격률': 0,
                '평균 점수': 0,
                '학과별 응시자 수': {},
                '학년별 응시자 수': {},
                '등급별 분포': {}
            }

    def create_student_progress_plots(self, email):
        """학생의 회차별 성과를 시각화합니다."""
        try:
            progress_df = self.get_student_progress(email)
            if progress_df.empty:
                return None, None, None

            # 점수 추이 그래프
            score_fig = self._create_score_trend_plot(progress_df)

            # 등급 변화 그래프
            grade_fig = self._create_grade_trend_plot(progress_df)

            # 성과 요약 테이블
            summary_df = self._create_performance_summary(progress_df)

            return score_fig, grade_fig, summary_df
        except Exception as e:
            st.error(f"학생 성과 시각화 중 오류 발생: {e}")
            return None, None, None

    def _create_score_trend_plot(self, progress_df):
        """점수 추이 그래프를 생성합니다."""
        score_fig = go.Figure()
        score_fig.add_trace(go.Scatter(
            x=progress_df['회차'],
            y=progress_df['총점'],
            mode='lines+markers+text',
            name='점수',
            text=progress_df['총점'].round(1),
            textposition='top center',
            line=dict(color='blue'),
            marker=dict(color=['green' if x == '합격' else 'red' for x in progress_df['합격여부']], size=12)
        ))
        score_fig.update_layout(title='회차별 점수 추이', xaxis_title='회차', yaxis_title='점수', showlegend=False)
        return score_fig

    def _create_grade_trend_plot(self, progress_df):
        """등급 변화 그래프를 생성합니다."""
        grade_fig = go.Figure()
        grade_fig.add_trace(go.Scatter(
            x=progress_df['회차'],
            y=progress_df['등급'],
            mode='lines+markers+text',
            text=progress_df['등급'],
            textposition='top center',
            line=dict(color='purple'),
            marker=dict(size=12)
        ))
        grade_fig.update_layout(title='회차별 등급 변화', xaxis_title='회차', yaxis_title='등급', showlegend=False)
        return grade_fig

    def _create_performance_summary(self, progress_df):
        """성과 요약 테이블을 생성합니다."""
        return pd.DataFrame({
            '지표': ['응시 횟수', '평균 점수', '최고 점수', '최저 점수', '합격 횟수'],
            '값': [
                len(progress_df),
                progress_df['총점'].mean().round(1),
                progress_df['총점'].max().round(1),
                progress_df['총점'].min().round(1),
                (progress_df['합격여부'] == '합격').sum()
            ]
        })

def main():
    st.set_page_config(page_title="닥코(닥치고 코딩)", layout="wide")
    
    st.title("코딩 역량 테스트")
    
    # 모니터링 객체 생성
    monitor = CodingTestMonitor()
    
    # 파일 업로드
    st.sidebar.header("데이터 업로드")
    uploaded_file = st.sidebar.selectbox(
        "테스트 결과 파일 선택",
        [
            '부산대학교 PCC_1회 응시 결과.csv',
            '부산대학교 PCC_2회 응시 결과.csv',
            '부산대학교 PCC_3회 응시 결과.csv',
            '부산대학교 PCC_4회 응시 결과.csv'
        ]
    )

    if uploaded_file:
        try:
            file = open(uploaded_file, 'r')
            if monitor.load_data(file):
                st.sidebar.success("데이터 로드 완료!")
        except Exception as e:
            st.error(f"파일 로드 중 오류 발생: {e}")
    
    if not monitor.data.empty:
        try:
            # 필터링 옵션
            st.sidebar.header("데이터 필터링")
            departments = sorted(monitor.data['학과'].unique().tolist())
            selected_dept = st.sidebar.multiselect("학과 선택 (다중 선택 가능)", departments)
            years = [''] + sorted(monitor.data['학년'].unique().tolist())
            selected_year = st.sidebar.selectbox("학년 선택", years)
            pass_status = [''] + sorted(monitor.data['합격여부'].unique().tolist())
            selected_status = st.sidebar.selectbox("합격여부 선택", pass_status)
            levels = [''] + sorted(monitor.data['등급(Lv.)'].unique().tolist())
            selected_level = st.sidebar.selectbox("등급 선택", levels)
            subjects = [''] + sorted(monitor.data['시험과목'].unique().tolist())
            selected_subject = st.sidebar.selectbox("시험과목 선택", subjects)
            
            # 필터 적용
            filters = {
                '학과': selected_dept,
                '학년': selected_year,
                '합격여부': selected_status,
                '등급(Lv.)': selected_level,
                '시험과목': selected_subject
            }
            filters = {k: v for k, v in filters.items() if v}
            filtered_data = monitor.filter_data(filters)
            
            # 기본 통계 표시
            st.header("기본 통계")
            stats = monitor.get_statistics(filtered_data)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 응시자 수", f"{stats['총 응시자 수']}명")
            with col2:
                st.metric("합격률", f"{stats['합격률']:.1f}%")
            with col3:
                st.metric("평균 점수", f"{stats['평균 점수']:.1f}점")
            
            # 시각화
            st.header("데이터 시각화")
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(monitor.create_score_distribution_plot(filtered_data), use_container_width=True)
                st.plotly_chart(monitor.create_department_average_score_plot(filtered_data), use_container_width=True)
                st.plotly_chart(monitor.create_department_pass_rate_plot(filtered_data), use_container_width=True)
            with col2:
                st.plotly_chart(monitor.create_subject_average_score_plot(filtered_data), use_container_width=True)
                st.plotly_chart(monitor.create_subject_pass_rate_plot(filtered_data), use_container_width=True)
                st.plotly_chart(monitor.create_grade_distribution_plot(filtered_data), use_container_width=True)
            
            # 데이터 테이블 표시
            st.header("상세 데이터")
            st.dataframe(filtered_data)
            
            # 데이터 다운로드 버튼
            if st.button("필터링된 데이터 다운로드"):
                output = pd.ExcelWriter('filtered_test_results.xlsx', engine='openpyxl')
                filtered_data.to_excel(output, index=False)
                output.close()
                
                with open('filtered_test_results.xlsx', 'rb') as f:
                    st.download_button(
                        label="Excel 파일 다운로드",
                        data=f,
                        file_name="filtered_test_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            # 고급 분석 섹션
            st.header("전체 회차")
            tab1, tab2 = st.tabs(["성과 분포", "상세 통계"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("전체 회차 응시자 현황")
                    if monitor.load_all_rounds_data():
                        participants_fig = monitor.create_performance_heatmap()
                        st.plotly_chart(participants_fig, use_container_width=True)
                    else:
                        st.warning("전체 회차 데이터를 로드할 수 없습니다.")
                
                with col2:
                    box_fig = monitor.create_score_box_plot()                    
            
            with tab2:
                advanced_stats = monitor.calculate_advanced_statistics(filtered_data)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("표준편차", f"{advanced_stats.get('표준편차', 0):.1f}")
                    st.metric("중앙값", f"{advanced_stats.get('중앙값', 0):.1f}")
                with col2:
                    st.metric("최고점수", f"{advanced_stats.get('최고점수', 0):.1f}")
                    st.metric("최저점수", f"{advanced_stats.get('최저점수', 0):.1f}")        
                                  
            st.header("학생별 성과 분석")
            if monitor.load_all_rounds_data():
                multiple_test_students = monitor.get_multiple_test_students()
                if not multiple_test_students.empty:
                    st.subheader("3회 이상 응시자 목록")
                    st.dataframe(
                        multiple_test_students,
                        column_config={
                            "이메일": "이메일",
                            "학과": "학과",
                            "학번": "학번",
                            "응시횟수": st.column_config.NumberColumn("응시횟수", help="전체 응시 횟수")
                        },
                        hide_index=True
                    )
                    
                    selected_email = st.selectbox(
                        "분석할 학생 선택",
                        options=multiple_test_students['이메일'].tolist(),
                        format_func=lambda x: f"{x} ({multiple_test_students[multiple_test_students['이메일']==x]['학과'].iloc[0]} - {multiple_test_students[multiple_test_students['이메일']==x]['학번'].iloc[0]})"
                    )
                    
                    if selected_email:
                        score_fig, grade_fig, summary_df = monitor.create_student_progress_plots(selected_email)
                        
                        if score_fig and grade_fig and summary_df is not None:
                            st.subheader("성과 요약")
                            st.dataframe(summary_df, hide_index=True)
                            col1, col2 = st.columns(2)
                            with col1:
                                st.plotly_chart(score_fig, use_container_width=True)
                            with col2:
                                st.plotly_chart(grade_fig, use_container_width=True)
                            
                            st.subheader("상세 회차별 데이터")
                            progress_data = monitor.get_student_progress(selected_email)
                            st.dataframe(progress_data)
                else:
                    st.warning("2회 이상 응시한 학생이 없습니다.")
                    
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")
            st.info("데이터 형식을 확인해주세요.")
    
    else:
        st.warning("업로드된 파일에 데이터가 없습니다.")

if __name__ == "__main__":
    main()
