from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Students
from .serializers import StudentsSerializer

class StudentsAPIView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # Check if teacher_id is provided as a query parameter
        teacher_id = request.query_params.get('teacher_id', None)

        if teacher_id:
            # If teacher_id is provided, filter students by teacher ID
            students = Students.objects.filter(teacher_id=teacher_id)
        else:
            # Otherwise, return all students
            students = Students.objects.all()

        serializer = StudentsSerializer(students, many=True)
        return Response({'results':serializer.data}, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        # Fetch a single student record by ID
        student_id = kwargs.get('pk')
        try:
            student = Students.objects.get(pk=student_id)
        except Students.DoesNotExist:
            return Response({'message': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentsSerializer(student)
        return Response({"results":serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # Create a new student record
        serializer = StudentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Student Created Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # Update an existing student record by ID
        student_id = kwargs.get('pk')
        try:
            student = Students.objects.get(pk=student_id)
        except Students.DoesNotExist:
            return Response({'detail': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentsSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Student Details Updated Successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        # Delete a student record by ID
        student_id = kwargs.get('pk')
        try:
            student = Students.objects.get(pk=student_id)
        except Students.DoesNotExist:
            return Response({'message': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)

        student.delete()
        return Response({'message': 'Student deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)